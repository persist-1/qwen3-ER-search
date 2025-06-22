#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web删除功能测试脚本
测试VectorDBViewer类的删除方法
"""

import sys
import os
import chromadb
from chromadb.config import Settings
import torch

# 添加web目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'web'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

def test_web_delete():
    """测试Web界面的删除功能"""
    try:
        # 导入VectorDBViewer
        from vector_db_viewer import VectorDBViewer
        
        # 创建viewer实例
        viewer = VectorDBViewer("vector_db", "documents")
        print("✅ 成功创建VectorDBViewer实例")
        
        # 导入embedding模型
        from test_qwen3_embedding import Qwen3Embedding
        
        # 初始化模型
        model_path = "models/Qwen3-Embedding-0.6B/Qwen/Qwen3-Embedding-0.6B"
        embedding_model = Qwen3Embedding(model_path)
        print("✅ 成功加载embedding模型")
        
        # 先添加一个测试文档
        test_document = """
        这是一个用于测试Web删除功能的文档。
        测试VectorDBViewer的delete_document方法。
        """
        
        chunks = [test_document.strip()]
        
        # 生成向量
        with torch.inference_mode():
            embeddings = embedding_model.encode(chunks, is_query=False)
        
        # 添加到数据库
        viewer.collection.add(
            documents=chunks,
            embeddings=embeddings.cpu().numpy().tolist(),
            metadatas=[{
                "source": "web_delete_test",
                "category": "test",
                "language": "zh",
                "document_id": "web_delete_test_doc",
                "chunk_index": 0,
                "chunk_length": len(test_document)
            }],
            ids=["web_delete_test_doc_chunk_0"]
        )
        
        print("✅ 成功添加测试文档")
        
        # 验证文档存在
        results = viewer.collection.get(ids=["web_delete_test_doc_chunk_0"])
        if results['ids']:
            print(f"✅ 验证文档存在: {results['ids'][0]}")
        else:
            print("❌ 文档添加失败")
            return False
        
        # 测试VectorDBViewer的删除方法
        print("🔄 开始测试VectorDBViewer删除功能...")
        
        # 使用viewer的delete_document方法
        success = viewer.delete_document("web_delete_test_doc")
        
        if success:
            print("✅ VectorDBViewer删除方法执行成功")
            
            # 验证删除结果
            verify_results = viewer.collection.get(where={"document_id": "web_delete_test_doc"})
            if not verify_results['ids']:
                print("✅ 文档已成功从数据库中删除")
                return True
            else:
                print("❌ 文档删除验证失败")
                return False
        else:
            print("❌ VectorDBViewer删除方法执行失败")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试Web删除功能...")
    success = test_web_delete()
    if success:
        print("🎉 Web删除功能测试通过！")
    else:
        print("💥 Web删除功能测试失败！") 