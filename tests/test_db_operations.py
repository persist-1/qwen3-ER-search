#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试向量数据库的删除和新增功能
"""

import chromadb
from chromadb.config import Settings
from datetime import datetime
import time

def test_database_operations():
    """测试数据库操作"""
    print("🧪 开始测试向量数据库操作...")
    
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
    
    # 1. 查看当前数据库状态
    print("\n📊 当前数据库状态:")
    count = collection.count()
    print(f"   总文档块数: {count}")
    
    if count > 0:
        all_results = collection.get()
        document_ids = set()
        for metadata in all_results['metadatas']:
            if metadata and 'document_id' in metadata:
                document_ids.add(metadata['document_id'])
        
        print(f"   唯一文档数: {len(document_ids)}")
        print(f"   文档ID列表: {list(document_ids)}")
    
    # 2. 测试新增功能
    print("\n📝 测试新增功能...")
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
        
        # 添加到数据库
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
        new_count = collection.count()
        print(f"   添加后总块数: {new_count}")
        
    except Exception as e:
        print(f"❌ 新增功能测试失败: {e}")
    
    # 3. 测试删除功能
    print("\n🗑️ 测试删除功能...")
    try:
        # 查找要删除的文档
        results = collection.get(where={"document_id": test_doc_id})
        
        if results['ids']:
            print(f"   找到要删除的文档: {test_doc_id}")
            print(f"   包含 {len(results['ids'])} 个块")
            
            # 删除文档
            collection.delete(ids=results['ids'])
            print(f"✅ 成功删除文档: {test_doc_id}")
            
            # 验证删除结果
            final_count = collection.count()
            print(f"   删除后总块数: {final_count}")
            
            if final_count == count:
                print("✅ 删除功能正常：文档已成功删除")
            else:
                print("⚠️ 删除功能异常：块数不匹配")
        else:
            print(f"❌ 未找到要删除的文档: {test_doc_id}")
            
    except Exception as e:
        print(f"❌ 删除功能测试失败: {e}")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    test_database_operations() 