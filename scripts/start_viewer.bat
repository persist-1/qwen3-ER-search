@echo off
echo 启动向量数据库可视化工具...
echo.

REM 激活虚拟环境
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo 虚拟环境已激活
) else (
    echo 警告: 未找到虚拟环境，使用系统Python
)

REM 启动Streamlit应用
echo 正在启动Web界面...
streamlit run web\vector_db_viewer.py

pause 