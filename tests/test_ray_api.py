#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ray Serve API 测试脚本
演示如何使用部署的Qwen3 Embedding和Reranker服务
"""

import requests
import json
import time
from typing import List

class RayAPIClient:
    def __init__(self, base_url: str = "http://localhost:4008"):
        self.base_url = base_url
        
    def test_embedding_api(self, texts: List[str], is_query: bool = False):
        """测试Embedding API"""
        url = f"{self.base_url}/embedding/api"
        payload = {
            "input": texts,
            "is_query": is_query
        }
        
        print(f"🔍 测试Embedding API...")
        print(f"   输入文本: {texts}")
        print(f"   是否为查询: {is_query}")
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Embedding API 成功!")
            print(f"   输出维度: {len(result)} x {len(result[0]) if result else 0}")
            print(f"   前5个向量值: {result[0][:5] if result else []}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Embedding API 失败: {e}")
            return None
    
    def test_reranker_api(self, questions: List[str], texts: List[str]):
        """测试Reranker API"""
        url = f"{self.base_url}/reranker/api"
        payload = {
            "questions": questions,
            "texts": texts
        }
        
        print(f"\n🎯 测试Reranker API...")
        print(f"   查询: {questions}")
        print(f"   文档: {texts}")
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Reranker API 成功!")
            print(f"   相关性分数: {result}")
            
            # 显示排序结果
            pairs = list(zip(questions, texts, result))
            sorted_pairs = sorted(pairs, key=lambda x: x[2], reverse=True)
            
            print(f"   排序结果:")
            for i, (q, t, score) in enumerate(sorted_pairs, 1):
                print(f"     {i}. 分数={score:.4f}, 查询='{q[:30]}...', 文档='{t[:50]}...'")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Reranker API 失败: {e}")
            return None
    
    def test_hybrid_search(self, query: str, documents: List[str]):
        """测试混合搜索流程"""
        print(f"\n🚀 测试混合搜索流程...")
        print(f"   查询: {query}")
        print(f"   文档数量: {len(documents)}")
        
        # 1. 使用Embedding进行粗筛
        print(f"\n   第一步: Embedding粗筛")
        query_embedding = self.test_embedding_api([query], is_query=True)
        doc_embeddings = self.test_embedding_api(documents, is_query=False)
        
        if not query_embedding or not doc_embeddings:
            print("❌ Embedding阶段失败")
            return
        
        # 2. 使用Reranker进行精筛
        print(f"\n   第二步: Reranker精筛")
        questions = [query] * len(documents)
        reranker_scores = self.test_reranker_api(questions, documents)
        
        if not reranker_scores:
            print("❌ Reranker阶段失败")
            return
        
        # 3. 显示最终结果
        print(f"\n   第三步: 最终排序结果")
        results = list(zip(documents, reranker_scores))
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
        
        for i, (doc, score) in enumerate(sorted_results[:3], 1):
            print(f"     {i}. 分数={score:.4f}, 文档='{doc[:80]}...'")

def main():
    """主函数"""
    print("=" * 80)
    print("🎯 Ray Serve API 测试")
    print("=" * 80)
    
    # 初始化客户端
    client = RayAPIClient()
    
    # 测试数据
    test_query = "机器学习算法"
    test_documents = [
        "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习。",
        "深度学习是机器学习的一个子领域，使用神经网络进行特征学习。",
        "自然语言处理是AI的重要应用，用于理解和生成人类语言。",
        "计算机视觉技术可以识别和分析图像中的内容。",
        "强化学习通过与环境交互来学习最优策略。"
    ]
    
    # 测试各个API
    print("\n1️⃣ 测试Embedding API")
    client.test_embedding_api(["这是一个测试文本"], is_query=True)
    
    print("\n2️⃣ 测试Reranker API")
    client.test_reranker_api(
        ["机器学习"], 
        ["机器学习算法", "深度学习技术", "自然语言处理"]
    )
    
    print("\n3️⃣ 测试混合搜索")
    client.test_hybrid_search(test_query, test_documents)
    
    print("\n" + "=" * 80)
    print("✅ 测试完成!")
    print("=" * 80)

if __name__ == "__main__":
    main() 