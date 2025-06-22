# 启动向量数据库可视化工具
Write-Host "启动向量数据库可视化工具..." -ForegroundColor Green
Write-Host ""

# 检查虚拟环境
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "激活虚拟环境..." -ForegroundColor Yellow
    & ".venv\Scripts\Activate.ps1"
    Write-Host "虚拟环境已激活" -ForegroundColor Green
} else {
    Write-Host "警告: 未找到虚拟环境，使用系统Python" -ForegroundColor Yellow
}

# 启动Streamlit应用
Write-Host "正在启动Web界面..." -ForegroundColor Cyan
Write-Host "请等待浏览器自动打开，或手动访问: http://localhost:8501" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Cyan
Write-Host ""

try {
    streamlit run web\vector_db_viewer.py --server.port 8501
} catch {
    Write-Host "启动失败: $_" -ForegroundColor Red
    Read-Host "按任意键退出"
} 