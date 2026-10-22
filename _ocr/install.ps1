# 安装 CUDA 版 PyTorch + MinerU；缓存全部放 E:，避免占用 C: 剩余空间
$ErrorActionPreference = 'Continue'
$env:PIP_CACHE_DIR = 'E:\dsh_cache\pip'
$env:TEMP = 'E:\dsh_cache\tmp'
$env:TMP  = 'E:\dsh_cache\tmp'
New-Item -ItemType Directory -Force -Path 'E:\dsh_cache\pip', 'E:\dsh_cache\tmp' | Out-Null

Write-Host "=== [1/3] install CUDA torch (cu130) ===" -ForegroundColor Cyan
python -m pip install --no-input --index-url https://download.pytorch.org/whl/cu130 "torch==2.12.1+cu130" torchvision
Write-Host "torch step exit=$LASTEXITCODE" -ForegroundColor Yellow

Write-Host "=== [2/3] verify CUDA ===" -ForegroundColor Cyan
python -c "import torch; print('torch', torch.__version__, 'cuda_avail', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')"

Write-Host "=== [3/3] install mineru[core] ===" -ForegroundColor Cyan
python -m pip install --no-input -U "mineru[core]"
Write-Host "mineru step exit=$LASTEXITCODE" -ForegroundColor Yellow

Write-Host "=== final verify ===" -ForegroundColor Cyan
python -c "import torch, mineru; print('torch', torch.__version__, 'cuda', torch.cuda.is_available()); print('mineru', getattr(mineru,'__version__','?'))"
Write-Host "=== DONE ===" -ForegroundColor Green
