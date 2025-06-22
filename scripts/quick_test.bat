@echo off
echo 运行快速测试...
echo.

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 运行基础测试
echo 1. 测试文档添加功能...
python tests\test_add_document_simple.py

echo.
echo 2. 测试数据库操作...
python tests\test_db_operations.py

echo.
echo 测试完成！
pause 