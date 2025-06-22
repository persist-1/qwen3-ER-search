# Qwen3 模型下载脚本 (PowerShell版本)
# 作者: Assistant
# 日期: 2025-06-21

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Qwen3 模型下载脚本 (PowerShell版本)" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# 创建models目录
Write-Host "1. 创建models目录..." -ForegroundColor Yellow
if (!(Test-Path "models")) {
    New-Item -ItemType Directory -Path "models"
}
Write-Host "✅ models目录创建完成" -ForegroundColor Green

# 安装modelscope
Write-Host "2. 安装modelscope..." -ForegroundColor Yellow
python -m pip install modelscope
Write-Host "✅ modelscope安装完成" -ForegroundColor Green

# 下载Qwen3-Embedding-0.6B模型
Write-Host "3. 下载Qwen3-Embedding-0.6B模型..." -ForegroundColor Yellow
python -c "from modelscope import snapshot_download; snapshot_download('Qwen/Qwen3-Embedding-0.6B', cache_dir='./models/Qwen3-Embedding-0.6B')"
Write-Host "✅ Qwen3-Embedding-0.6B模型下载完成" -ForegroundColor Green

# 下载Qwen3-Reranker-0.6B模型
Write-Host "4. 下载Qwen3-Reranker-0.6B模型..." -ForegroundColor Yellow
python -c "from modelscope import snapshot_download; snapshot_download('Qwen/Qwen3-Reranker-0.6B', cache_dir='./models/Qwen3-Reranker-0.6B')"
Write-Host "✅ Qwen3-Reranker-0.6B模型下载完成" -ForegroundColor Green

# 验证模型文件
Write-Host "5. 验证模型文件..." -ForegroundColor Yellow
Write-Host "检查Embedding模型文件:" -ForegroundColor Cyan
if (Test-Path "models\Qwen3-Embedding-0.6B\Qwen\Qwen3-Embedding-0.6B\") {
    Get-ChildItem "models\Qwen3-Embedding-0.6B\Qwen\Qwen3-Embedding-0.6B\" | Select-Object Name, Length | Format-Table
}

Write-Host "检查Reranker模型文件:" -ForegroundColor Cyan
if (Test-Path "models\Qwen3-Reranker-0.6B\Qwen\Qwen3-Reranker-0.6B\") {
    Get-ChildItem "models\Qwen3-Reranker-0.6B\Qwen\Qwen3-Reranker-0.6B\" | Select-Object Name, Length | Format-Table
}

Write-Host "==========================================" -ForegroundColor Green
Write-Host "模型下载完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "模型路径:" -ForegroundColor White
Write-Host "- Embedding: models\Qwen3-Embedding-0.6B\Qwen\Qwen3-Embedding-0.6B\" -ForegroundColor White
Write-Host "- Reranker: models\Qwen3-Reranker-0.6B\Qwen\Qwen3-Reranker-0.6B\" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Green

Read-Host "按回车键退出" 