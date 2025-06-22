#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的文档添加测试脚本
"""

import sys
import os
import chromadb
from chromadb.config import Settings
import torch

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

def test_add_document():
    """测试添加文档功能"""
    try:
        # 连接到数据库
        client = chromadb.PersistentClient(
            path="vector_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 获取collection
        collection = client.get_collection(name="documents")
        print("✅ 成功连接到数据库")
        
        # 导入embedding模型
        from test_qwen3_embedding import Qwen3Embedding
        
        # 初始化模型
        model_path = "models/Qwen3-Embedding-0.6B/Qwen/Qwen3-Embedding-0.6B"
        embedding_model = Qwen3Embedding(model_path)
        print("✅ 成功加载embedding模型")
        
        # 测试文档
        test_document = """
        这是一个测试文档，用于验证向量数据库的添加功能。
        文档包含了关于机器学习和人工智能的内容。
        我们正在测试Qwen3-Embedding模型是否能正确生成1024维向量。
        """
        
        # 分割文档
        chunks = [test_document.strip()]
        
        # 生成向量
        with torch.inference_mode():
            embeddings = embedding_model.encode(chunks, is_query=False)
        
        print(f"✅ 成功生成向量，维度: {embeddings.shape}")
        
        # 准备元数据
        metadata = {
            "source": "test_script",
            "category": "test",
            "language": "zh",
            "document_id": "test_doc_001",
            "chunk_index": 0,
            "chunk_length": len(test_document)
        }
        
        # 添加到数据库
        collection.add(
            documents=chunks,
            embeddings=embeddings.cpu().numpy().tolist(),
            metadatas=[metadata],
            ids=["test_doc_001_chunk_0"]
        )
        
        print("✅ 成功添加文档到数据库")
        
        # 验证添加结果
        results = collection.get(ids=["test_doc_001_chunk_0"])
        print(f"✅ 验证成功，文档ID: {results['ids'][0]}")
        print(f"文档内容: {results['documents'][0][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试文档添加功能...")
    success = test_add_document()
    if success:
        print("🎉 所有测试通过！")
    else:
        print("💥 测试失败！") 