@echo off
echo 启动向量数据库可视化工具...
echo.

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 启动Streamlit应用
streamlit run web\vector_db_viewer.py

pause 