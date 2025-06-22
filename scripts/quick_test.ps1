# 快速测试脚本
Write-Host "运行快速测试..." -ForegroundColor Green
Write-Host ""

# 激活虚拟环境
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
    Write-Host "虚拟环境已激活" -ForegroundColor Yellow
}

# 运行基础测试
Write-Host "1. 测试文档添加功能..." -ForegroundColor Cyan
python tests\test_add_document_simple.py

Write-Host ""
Write-Host "2. 测试数据库操作..." -ForegroundColor Cyan
python tests\test_db_operations.py

Write-Host ""
Write-Host "测试完成！" -ForegroundColor Green 