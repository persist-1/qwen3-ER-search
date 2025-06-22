#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新增文档功能
"""

import chromadb
from chromadb.config import Settings
from datetime import datetime
import time

def test_add_document():
    """测试新增文档功能"""
    print("🧪 测试新增文档功能...")
    
    # 连接到数据库
    client = chromadb.PersistentClient(
        path="vector_db",
        settings=Settings(anonymized_telemetry=False)
    )
    
    try:
        collection = client.get_collection(name="documents")
        print("✅ 成功连接到数据库")
    except Exception as e:
        print(f"❌ 连接数据库失败: {e}")
        return
    
    # 查看当前状态
    count_before = collection.count()
    print(f"📊 添加前总块数: {count_before}")
    
    # 测试添加文档
    test_doc_id = f"test_doc_{int(time.time())}"
    test_text = "这是一个测试文档。用于验证新增功能是否正常工作。包含多个句子。"
    
    try:
        # 分割文本
        chunks = [test_text]
        metadata = {
            "source": "test",
            "category": "test",
            "language": "zh",
            "timestamp": datetime.now().isoformat(),
            "file_name": f"{test_doc_id}.txt"
        }
        
        # 添加到数据库（使用Chroma的默认embedding）
        collection.add(
            documents=chunks,
            metadatas=[{
                **metadata,
                "document_id": test_doc_id,
                "chunk_index": 0,
                "chunk_length": len(test_text)
            }],
            ids=[f"{test_doc_id}_chunk_0"]
        )
        
        print(f"✅ 成功添加测试文档: {test_doc_id}")
        
        # 验证添加结果
        count_after = collection.count()
        print(f"📊 添加后总块数: {count_after}")
        
        if count_after > count_before:
            print("✅ 新增功能正常：文档已成功添加")
        else:
            print("❌ 新增功能异常：块数没有增加")
            
    except Exception as e:
        print(f"❌ 新增功能测试失败: {e}")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    test_add_document() 