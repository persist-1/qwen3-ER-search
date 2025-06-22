#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除功能测试脚本
"""

import sys
import os
import json
import numpy as np
from typing import List, Tuple, Dict, Optional
import chromadb
from chromadb.config import Settings
import torch
from datetime import datetime
import uuid
from pathlib import Path

# Add the src directory to the path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.test_qwen3_embedding import Qwen3Embedding

def test_delete_function():
    """测试删除功能"""
    try:
        # 连接到数据库
        client = chromadb.PersistentClient(
            path="vector_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 获取collection
        collection = client.get_collection(name="documents")
        print("✅ 成功连接到数据库")
        
        # 初始化模型
        model_path = "models/Qwen3-Embedding-0.6B/Qwen/Qwen3-Embedding-0.6B"
        embedding_model = Qwen3Embedding(model_path)
        print("✅ 成功加载embedding模型")
        
        # 先添加一个测试文档用于删除
        test_document = """
        这是一个用于测试删除功能的文档。
        删除后应该从数据库中完全移除。
        """
        
        chunks = [test_document.strip()]
        
        # 生成向量
        with torch.inference_mode():
            embeddings = embedding_model.encode(chunks, is_query=False)
        
        # 添加到数据库
        collection.add(
            documents=chunks,
            embeddings=embeddings.cpu().numpy().tolist(),
            metadatas=[{
                "source": "delete_test",
                "category": "test",
                "language": "zh",
                "document_id": "delete_test_doc",
                "chunk_index": 0,
                "chunk_length": len(test_document)
            }],
            ids=["delete_test_doc_chunk_0"]
        )
        
        print("✅ 成功添加测试文档")
        
        # 验证文档存在
        results = collection.get(ids=["delete_test_doc_chunk_0"])
        if results['ids']:
            print(f"✅ 验证文档存在: {results['ids'][0]}")
        else:
            print("❌ 文档添加失败")
            return False
        
        # 测试删除功能
        print("🔄 开始测试删除功能...")
        
        # 查找要删除的文档
        results = collection.get(where={"document_id": "delete_test_doc"})
        
        if not results['ids']:
            print("❌ 未找到要删除的文档")
            return False
        
        print(f"✅ 找到 {len(results['ids'])} 个文档块")
        
        # 删除文档
        collection.delete(ids=results['ids'])
        print("✅ 删除操作执行完成")
        
        # 验证删除结果
        verify_results = collection.get(ids=results['ids'])
        if not verify_results['ids']:
            print("✅ 文档已成功删除")
        else:
            print("❌ 文档删除失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试删除功能...")
    success = test_delete_function()
    if success:
        print("🎉 删除功能测试通过！")
    else:
        print("💥 删除功能测试失败！") 