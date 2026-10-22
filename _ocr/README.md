# `_ocr/` —— 408 教材的 PDF→Markdown 转换流水线

四本王道教材的 OCR 产物、转换脚本与校验报告。**2026-10-22 从 `408\_ocr` 整体移到工作区根**，
脚本里的路径已同步改成「随本目录位置自动推导」，不再写死 `C:\Users\天元\Desktop\408`。

## 目录

```
_ocr/
├── *.py                 转换 / 清洗 / 校验脚本（99 个）
├── *.json               书签 TOC、清理报告、罗马数字核验结果
├── *.log                历史运行日志（保留原样，内含旧路径属正常记录）
├── {os,ds,co,cn}_full/   MinerU 原始产物 zip（每本一个）
├── ds_full_x/           数据结构已解压的 MinerU 产物（markdown / structured_content / images）
├── models/              EasyOCR 权重（craft_mlt_25k.pth / zh_sim_g2.pth）
└── work/                中间产物目录（*_Markdown 等，可安全删除/重建）
```

## 脚本里的路径约定

每个脚本开头都有同一段常量，**按 `__file__` 推导，整个目录可自由搬迁**：

```python
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物
```

（常量名故意避开 `BOOKS` / `WORK` —— 多个脚本自己就拿这两个名字当列表/字典用。）

旧的 `"_ocr/xxx"` 相对写法保留原样：`os.path.join(WS, "_ocr", "toc_ds.json")` 现在正好指向本目录。

## 路径映射（迁移前后）

| 旧位置（已失效） | 现在 |
|---|---|
| `Desktop\408\_ocr\*` | `11408\_ocr\*` |
| `Desktop\408\27王道《…》高清带书签.pdf` | `11408\408\…pdf` |
| `Desktop\408\<科目>_清理版\` | `11408\408\<科目>\` |
| `Desktop\408\<科目>_Markdown\` | `11408\_ocr\work\<科目>_Markdown\` |

## 流水线顺序

| 阶段 | 脚本 | 输入 → 输出 |
|---|---|---|
| 取书签 | `export_toc.py`、`probe_books.py` | `408\*.pdf` → `_ocr\toc*.json` |
| 版面解析 | `parse_all.py`、`ds_safe_run.py` | `408\*.pdf` → `_ocr\<slug>_full\*.zip` |
| 组卷（层级对齐） | `build_book.py <os\|ds\|co\|cn>` | zip + toc + pdf → `_ocr\work\<科目>_Markdown\` |
| 清洗分章 | `clean_book.py <os\|ds\|cn>`；组成原理用 `clean_co.py` | `work\<科目>_Markdown\` → `408\<科目>\` |
| 恢复【考纲内容】 | `fix_kaogang2.py` | `408\<科目>\`（原地） |
| 摘出习题 | `extract_ex.py` | `408\<科目>\` → 同目录 `第N章 习题与解析.md` |
| 验收（只读） | `verify_rest.py`、`final_all2.py` | `408\<科目>\` + toc → 报告 |
| 生成 README | `gen_readme_all.py` | `408\<科目>\` + toc → 同目录 `README.md` |

## 注意

- **`clean_book.py` / `clean_co.py` / `fix_kaogang2.py` / `undo_kaogang.py` / `extract_ex.py` / `gen_readme_*.py` 会直接改写 `408\<科目>\`**。
  这几个是「重建成品」用的，重跑前先备份该目录；`verify_*.py`、`final_all2.py`、`check_*.py`、`look_*.py`、`diag_*.py` 是只读的。
- 组成原理走的是另一条线（`clean_co.py`），它的原始 Markdown 已不存在，重跑需要先从 zip 解压。
- `os_full_x\` 与 `ds_result.pkl` 已被删除，依赖它们的脚本（`diag2.py`、`diag_garbage.py`、`build_final.py`、`ds_export_fixed.py` 等）目前读不到输入。
- `install.ps1` 是装环境用的（CUDA 版 torch + `mineru[core]`），缓存刻意放在 `E:`，与本目录路径无关。
- 迁移前的 99 个脚本原样备份在 `%TEMP%\11408_ocr_py_backup\`。
