#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的数据库操作测试
"""

import chromadb
from chromadb.config import Settings
from datetime import datetime
import time

def simple_test():
    """简化的测试"""
    print("🧪 简化测试向量数据库操作...")
    
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
    count = collection.count()
    print(f"📊 当前总块数: {count}")
    
    if count > 0:
        all_results = collection.get()
        document_ids = set()
        for metadata in all_results['metadatas']:
            if metadata and 'document_id' in metadata:
                document_ids.add(metadata['document_id'])
        
        print(f"📄 当前文档: {list(document_ids)}")
    
    # 测试删除现有文档
    if count > 0:
        print("\n🗑️ 测试删除功能...")
        try:
            # 删除第一个文档
            first_doc_id = list(document_ids)[0]
            results = collection.get(where={"document_id": first_doc_id})
            
            if results['ids']:
                print(f"   删除文档: {first_doc_id}")
                collection.delete(ids=results['ids'])
                
                new_count = collection.count()
                print(f"   删除后块数: {new_count}")
                print("✅ 删除功能正常")
            else:
                print("❌ 未找到要删除的文档")
                
        except Exception as e:
            print(f"❌ 删除测试失败: {e}")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    simple_test() 