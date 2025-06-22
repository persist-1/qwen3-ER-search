@echo off
chcp 65001 >nul

echo ==========================================
echo Qwen3 模型下载脚本 (Windows版本)
echo ==========================================

REM 创建models目录
echo 1. 创建models目录...
if not exist "models" mkdir models
echo ✅ models目录创建完成

REM 安装modelscope
echo 2. 安装modelscope...
python -m pip install modelscope
echo ✅ modelscope安装完成

REM 下载Qwen3-Embedding-0.6B模型
echo 3. 下载Qwen3-Embedding-0.6B模型...
python -c "from modelscope import snapshot_download; snapshot_download('Qwen/Qwen3-Embedding-0.6B', cache_dir='./models/Qwen3-Embedding-0.6B')"
echo ✅ Qwen3-Embedding-0.6B模型下载完成

REM 下载Qwen3-Reranker-0.6B模型
echo 4. 下载Qwen3-Reranker-0.6B模型...
python -c "from modelscope import snapshot_download; snapshot_download('Qwen/Qwen3-Reranker-0.6B', cache_dir='./models/Qwen3-Reranker-0.6B')"
echo ✅ Qwen3-Reranker-0.6B模型下载完成

REM 验证模型文件
echo 5. 验证模型文件...
echo 检查Embedding模型文件:
dir models\Qwen3-Embedding-0.6B\Qwen\Qwen3-Embedding-0.6B\

echo 检查Reranker模型文件:
dir models\Qwen3-Reranker-0.6B\Qwen\Qwen3-Reranker-0.6B\

echo ==========================================
echo 模型下载完成！
echo ==========================================
echo 模型路径:
echo - Embedding: models\Qwen3-Embedding-0.6B\Qwen\Qwen3-Embedding-0.6B\
echo - Reranker: models\Qwen3-Reranker-0.6B\Qwen\Qwen3-Reranker-0.6B\
echo ==========================================

pause 