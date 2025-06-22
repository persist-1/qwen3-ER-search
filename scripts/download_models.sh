#!/bin/bash

# Qwen3 模型下载脚本
# 作者: Assistant
# 日期: 2025-06-21

echo "=========================================="
echo "Qwen3 模型下载脚本"
echo "=========================================="

# 创建models目录
echo "1. 创建models目录..."
mkdir -p models
echo "✅ models目录创建完成"

# 安装modelscope
echo "2. 安装modelscope..."
pip install modelscope
echo "✅ modelscope安装完成"

# 下载Qwen3-Embedding-0.6B模型
echo "3. 下载Qwen3-Embedding-0.6B模型..."
python -c "from modelscope import snapshot_download; snapshot_download('Qwen/Qwen3-Embedding-0.6B', cache_dir='./models/Qwen3-Embedding-0.6B')"
echo "✅ Qwen3-Embedding-0.6B模型下载完成"

# 下载Qwen3-Reranker-0.6B模型
echo "4. 下载Qwen3-Reranker-0.6B模型..."
python -c "from modelscope import snapshot_download; snapshot_download('Qwen/Qwen3-Reranker-0.6B', cache_dir='./models/Qwen3-Reranker-0.6B')"
echo "✅ Qwen3-Reranker-0.6B模型下载完成"

# 验证模型文件
echo "5. 验证模型文件..."
echo "检查Embedding模型文件:"
ls -la models/Qwen3-Embedding-0.6B/Qwen/Qwen3-Embedding-0.6B/ | head -10

echo "检查Reranker模型文件:"
ls -la models/Qwen3-Reranker-0.6B/Qwen/Qwen3-Reranker-0.6B/ | head -10

echo "=========================================="
echo "模型下载完成！"
echo "=========================================="
echo "模型路径:"
echo "- Embedding: models/Qwen3-Embedding-0.6B/Qwen/Qwen3-Embedding-0.6B/"
echo "- Reranker: models/Qwen3-Reranker-0.6B/Qwen/Qwen3-Reranker-0.6B/"
echo "==========================================" 