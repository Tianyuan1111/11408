# -*- coding: utf-8 -*-
"""
低内存模式解析《数据结构》，并带内存看门狗。

背景：默认 3 个 PDF 渲染进程 × 64 页窗口，峰值内存约 5-6 GB；
      上一轮在系统仅剩 6.4 GB 空闲时把机器压到内核崩溃。
本次措施：
  DOCVORTEX_PDF_RENDER_THREADS = 1     渲染进程 3 -> 1（内存峰值约降为 1/3）
  MINERU_PROCESSING_WINDOW_SIZE = 32   窗口 64 -> 32 页（每窗口内存减半）
  DOCVORTEX_PDF_RENDER_TIMEOUT = 1800  渲染超时 300 -> 1800 秒（变慢后不至于被超时杀掉）
  看门狗：空闲物理内存低于阈值即优雅中止，宁可重来也不让系统崩。
"""
import os, sys, time, ctypes, threading, subprocess

sys.stdout.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(line_buffering=True)

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
PDF = os.path.join(BOOKDIR, "27王道《数据结构》高清带书签.pdf")
OUT = os.path.join(WS, "_ocr", "ds_full")
LOG = os.path.join(WS, "_ocr", "ds_safe.log")
MINERU = r"E:\Python313\Scripts\mineru.exe"
MINERU_KIT = r"E:\Python313\Scripts\mineru-kit.exe"

ABORT_FREE_MB = 2000          # 空闲物理内存低于此值即中止
POLL_SEC = 5

ENV = dict(os.environ)
ENV.update({
    "MINERU_HOME": r"E:\dsh_cache\mineru",
    "PYTHONIOENCODING": "utf-8",
    "PYTHONUTF8": "1",
    "DOCVORTEX_PDF_RENDER_THREADS": "1",
    "MINERU_PROCESSING_WINDOW_SIZE": "32",
    "DOCVORTEX_PDF_RENDER_TIMEOUT": "1800",
})


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def mem_mb():
    m = MEMORYSTATUSEX()
    m.dwLength = ctypes.sizeof(m)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 1048576, m.ullAvailPageFile / 1048576


logf = open(LOG, "w", encoding="utf-8", buffering=1)


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line)
    logf.write(line + "\n")


stop_flag = threading.Event()
aborted = threading.Event()
min_free = [99999.0]


def watchdog():
    while not stop_flag.is_set():
        free, pf = mem_mb()
        min_free[0] = min(min_free[0], free)
        if free < ABORT_FREE_MB:
            log(f"!! 空闲内存 {free:.0f} MB 低于阈值 {ABORT_FREE_MB} MB —— 中止解析以保护系统")
            aborted.set()
            subprocess.run([MINERU, "server", "stop"], env=ENV,
                           capture_output=True, text=True, timeout=120)
            return
        time.sleep(POLL_SEC)


def main():
    # 0. 清掉可能残留的服务
    subprocess.run([MINERU, "server", "stop"], env=ENV, capture_output=True, text=True, timeout=120)
    time.sleep(3)

    free, pf = mem_mb()
    log(f"起始空闲内存 {free:.0f} MB，页面文件可用 {pf:.0f} MB")
    log("低内存配置: RENDER_THREADS=1, WINDOW_SIZE=32, RENDER_TIMEOUT=1800")

    # 1. 启动服务（渲染进程由它派生，必须让它继承这些环境变量）
    log("启动 mineru 服务 ...")
    r = subprocess.run([MINERU, "server", "start"], env=ENV, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=300)
    log(f"  server start rc={r.returncode} {(r.stdout or '').strip()[-120:]}")

    for i in range(20):
        time.sleep(30)
        if stop_flag.is_set():
            return
        s = subprocess.run([MINERU, "server", "status"], env=ENV, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=120)
        out = (s.stdout or "") + (s.stderr or "")
        free, _ = mem_mb()
        if "仍在启动中" not in out:
            log(f"服务就绪（等待 {(i+1)*30}s，空闲 {free:.0f} MB）")
            break
        log(f"  等待服务启动 {(i+1)*30}s，空闲 {free:.0f} MB")
    else:
        log("服务启动超时")
        return

    threading.Thread(target=watchdog, daemon=True).start()

    # 2. 解析
    log("开始解析 数据结构 (404 页) ...")
    t0 = time.time()
    cmd = [MINERU_KIT, "parse", PDF, "-o", OUT, "--pages", "all", "--tier", "basic", "-f", "zip"]
    with open(os.path.join(WS, "_ocr", "ds_safe_parse.log"), "w", encoding="utf-8") as pf_log:
        p = subprocess.Popen(cmd, env=ENV, stdout=pf_log, stderr=subprocess.STDOUT,
                             text=True, encoding="utf-8", errors="replace")
        while p.poll() is None:
            if aborted.is_set():
                p.kill()
                log("已终止解析进程")
                break
            time.sleep(10)
        rc = p.wait()

    dt = time.time() - t0
    stop_flag.set()
    free, _ = mem_mb()
    log(f"解析结束 rc={rc} 用时 {dt/60:.1f} 分钟")
    log(f"全程最低空闲内存 {min_free[0]:.0f} MB；结束时空闲 {free:.0f} MB")

    # 3. 结果核对
    zips = []
    if os.path.isdir(OUT):
        zips = [f for f in os.listdir(OUT) if f.lower().endswith(".zip")]
    log(f"产出 zip: {zips if zips else '无'}")
    if zips:
        for f in zips:
            log(f"  {f}  {os.path.getsize(os.path.join(OUT, f))/1048576:.1f} MB")
    else:
        tail = ""
        pl = os.path.join(WS, "_ocr", "ds_safe_parse.log")
        if os.path.exists(pl):
            with open(pl, encoding="utf-8", errors="replace") as fh:
                tail = "".join(fh.readlines()[-25:])
        log("解析日志尾部:\n" + tail)
    logf.close()


if __name__ == "__main__":
    main()
