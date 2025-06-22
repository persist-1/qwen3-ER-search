#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于向量数据库的混合PDF检索系统
使用Chroma向量数据库持久化存储文档向量
支持大规模文档检索和增量更新
"""

import fitz  # PyMuPDF
import numpy as np
from typing import List, Tuple, Dict, Optional
from test_qwen3_embedding import Qwen3Embedding
from test_qwen3_reranker import Qwen3Reranker
import torch
import re
import os
import json
import time
from datetime import datetime
import chromadb
from chromadb.config import Settings
import uuid

class HybridPDFRetrieverDB:
    def __init__(self, 
                 embedding_model_path: str = "models/Qwen3-Embedding-0.6B/Qwen/Qwen3-Embedding-0.6B",
                 reranker_model_path: str = "models/Qwen3-Reranker-0.6B/Qwen/Qwen3-Reranker-0.6B",
                 db_path: str = "vector_db",
                 collection_name: str = "documents"):
        """
        初始化基于向量数据库的混合PDF检索器
        Args:
            embedding_model_path: Qwen3 Embedding模型路径
            reranker_model_path: Qwen3 Reranker模型路径
            db_path: 向量数据库存储路径
            collection_name: 集合名称
        """
        print("正在加载Qwen3 Embedding模型...")
        self.embedding_model = Qwen3Embedding(embedding_model_path)
        print("Embedding模型加载完成！")
        
        print("正在加载Qwen3 Reranker模型...")
        self.reranker_model = Qwen3Reranker(
            model_name_or_path=reranker_model_path,
            instruction="Given the user query, retrieval the relevant passages",
            max_length=2048
        )
        print("Reranker模型加载完成！")
        
        # 初始化向量数据库
        print(f"正在初始化向量数据库: {db_path}")
        self.db_path = db_path
        self.collection_name = collection_name
        self._init_vector_db()
        
        self.chunk_size = 300
        self.documents = []
        self.document_metadata = {}
        
    def _init_vector_db(self):
        """初始化Chroma向量数据库"""
        try:
            # 创建数据库客户端
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 获取或创建集合
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                print(f"✅ 成功加载现有集合: {self.collection_name}")
                print(f"   现有文档数量: {self.collection.count()}")
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Qwen3混合检索系统文档集合"}
                )
                print(f"✅ 成功创建新集合: {self.collection_name}")
                
        except Exception as e:
            print(f"❌ 向量数据库初始化失败: {e}")
            raise
    
    def load_pdf(self, pdf_path: str, document_id: Optional[str] = None) -> List[str]:
        """
        加载PDF文件并提取文本
        Args:
            pdf_path: PDF文件路径
            document_id: 文档ID，如果不提供则自动生成
        """
        if document_id is None:
            document_id = str(uuid.uuid4())
            
        print(f"正在加载PDF文件: {pdf_path}")
        print(f"文档ID: {document_id}")
        
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                full_text += f"第{page_num + 1}页: " + text + "\n"
            
            doc.close()
            
            # 分割文本
            chunks = self._split_text(full_text)
            
            # 存储文档元数据
            self.document_metadata[document_id] = {
                "file_path": pdf_path,
                "file_name": os.path.basename(pdf_path),
                "total_chunks": len(chunks),
                "upload_time": datetime.now().isoformat(),
                "file_size": os.path.getsize(pdf_path)
            }
            
            print(f"成功提取 {len(chunks)} 个文本块")
            return chunks
            
        except Exception as e:
            print(f"加载PDF文件失败: {e}")
            return []
    
    def _split_text(self, text: str) -> List[str]:
        """将文本分割成小块"""
        sentences = re.split(r'[。！？；\n]', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + "。"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + "。"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def add_documents_to_db(self, documents: List[str], document_id: str, 
                           metadata: Optional[Dict] = None) -> bool:
        """
        将文档添加到向量数据库
        Args:
            documents: 文档文本列表
            document_id: 文档ID
            metadata: 额外元数据
        Returns:
            是否成功添加
        """
        if not documents:
            print("没有文档可以添加")
            return False
            
        try:
            print(f"正在将文档 {document_id} 添加到向量数据库...")
            
            # 生成文档向量
            with torch.inference_mode():
                embeddings = self.embedding_model.encode(documents, is_query=False)
            
            # 转换为numpy数组
            embeddings_np = embeddings.cpu().detach().numpy()
            
            # 生成唯一ID列表
            ids = [f"{document_id}_chunk_{i}" for i in range(len(documents))]
            
            # 准备元数据
            chunk_metadata = []
            for i, doc in enumerate(documents):
                chunk_meta = {
                    "document_id": document_id,
                    "chunk_index": i,
                    "chunk_length": len(doc),
                    "timestamp": datetime.now().isoformat()
                }
                if metadata:
                    chunk_meta.update(metadata)
                chunk_metadata.append(chunk_meta)
            
            # 添加到向量数据库
            self.collection.add(
                embeddings=embeddings_np.tolist(),
                documents=documents,
                metadatas=chunk_metadata,
                ids=ids
            )
            
            print(f"✅ 成功添加 {len(documents)} 个文档块到向量数据库")
            print(f"   向量维度: {embeddings_np.shape[1]}")
            print(f"   总文档数量: {self.collection.count()}")
            
            return True
            
        except Exception as e:
            print(f"❌ 添加文档到向量数据库失败: {e}")
            return False
    
    def search_similar_documents(self, query: str, top_k: int = 10, 
                                filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """
        在向量数据库中搜索相似文档
        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter_metadata: 过滤条件
        Returns:
            搜索结果列表
        """
        try:
            # 生成查询向量
            with torch.inference_mode():
                query_embedding = self.embedding_model.encode([query], is_query=True)
            
            query_embedding_np = query_embedding.cpu().detach().numpy()
            
            # 在向量数据库中搜索
            results = self.collection.query(
                query_embeddings=query_embedding_np.tolist(),
                n_results=top_k,
                where=filter_metadata
            )
            
            # 格式化结果
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'similarity': 1 - results['distances'][0][i]  # 转换为相似度
                }
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ 向量数据库搜索失败: {e}")
            return []
    
    def hybrid_search_db(self, query: str, top_k_embedding: int = 10, 
                        top_k_final: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """
        基于向量数据库的混合检索
        Args:
            query: 查询文本
            top_k_embedding: Embedding阶段候选数量
            top_k_final: 最终返回结果数量
            filter_metadata: 过滤条件
        Returns:
            最终结果列表
        """
        print(f"正在进行混合检索: {query}")
        print("="*50)
        
        # 第一阶段：向量数据库粗筛
        print("第一阶段：向量数据库粗筛")
        embedding_results = self.search_similar_documents(
            query, top_k_embedding, filter_metadata
        )
        
        if not embedding_results:
            print("❌ 向量数据库搜索无结果")
            return []
        
        print(f"向量数据库找到 {len(embedding_results)} 个候选文档:")
        for i, result in enumerate(embedding_results, 1):
            print(f"  候选{i}: 相似度={result['similarity']:.4f}, ID={result['id']}")
            print(f"    内容: {result['document'][:80]}...")
        
        # 第二阶段：Reranker精筛
        print(f"\n第二阶段：Reranker精筛")
        candidates = [result['document'] for result in embedding_results]
        pairs = [(query, doc) for doc in candidates]
        
        # 使用Reranker计算相关性分数
        reranker_scores = self.reranker_model.compute_scores(pairs)
        
        # 组合结果
        final_results = []
        for i, (result, reranker_score) in enumerate(zip(embedding_results, reranker_scores)):
            final_result = {
                'id': result['id'],
                'document': result['document'],
                'metadata': result['metadata'],
                'embedding_similarity': result['similarity'],
                'reranker_score': reranker_score,
                'final_score': reranker_score  # 使用Reranker分数作为最终分数
            }
            final_results.append(final_result)
        
        # 按最终分数排序
        final_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        print(f"Reranker阶段重新排序结果:")
        for i, result in enumerate(final_results[:top_k_final], 1):
            print(f"  排序{i}: Reranker分数={result['reranker_score']:.4f}, "
                  f"Embedding相似度={result['embedding_similarity']:.4f}, ID={result['id']}")
            print(f"    内容: {result['document'][:80]}...")
        
        return final_results[:top_k_final]
    
    def get_database_stats(self) -> Dict:
        """获取数据库统计信息"""
        try:
            count = self.collection.count()
            
            # 获取所有文档的元数据
            all_results = self.collection.get()
            
            # 统计文档ID
            document_ids = set()
            for metadata in all_results['metadatas']:
                if metadata and 'document_id' in metadata:
                    document_ids.add(metadata['document_id'])
            
            stats = {
                'total_chunks': count,
                'unique_documents': len(document_ids),
                'document_ids': list(document_ids),
                'collection_name': self.collection_name,
                'database_path': self.db_path
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ 获取数据库统计信息失败: {e}")
            return {}
    
    def delete_document(self, document_id: str) -> bool:
        """
        删除指定文档的所有块
        Args:
            document_id: 要删除的文档ID
        Returns:
            是否成功删除
        """
        try:
            # 查找所有属于该文档的块
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if not results['ids']:
                print(f"未找到文档ID为 {document_id} 的文档")
                return False
            
            # 删除这些块
            self.collection.delete(ids=results['ids'])
            
            print(f"✅ 成功删除文档 {document_id} 的 {len(results['ids'])} 个块")
            return True
            
        except Exception as e:
            print(f"❌ 删除文档失败: {e}")
            return False
    
    def update_document(self, document_id: str, new_documents: List[str], 
                       new_metadata: Optional[Dict] = None) -> bool:
        """
        更新指定文档
        Args:
            document_id: 文档ID
            new_documents: 新的文档内容
            new_metadata: 新的元数据
        Returns:
            是否成功更新
        """
        # 先删除旧文档
        if not self.delete_document(document_id):
            return False
        
        # 添加新文档
        return self.add_documents_to_db(new_documents, document_id, new_metadata)

def main():
    """主函数 - 演示使用向量数据库的混合检索系统"""
    
    # 初始化检索器
    retriever = HybridPDFRetrieverDB()
    
    # 显示数据库统计信息
    print("\n📊 数据库统计信息:")
    stats = retriever.get_database_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # 加载PDF文档
    pdf_path = r"C:\Users\sanrome\Documents\三郎白底通用简历-zh.pdf"
    document_id = "resume_zhang"
    
    documents = retriever.load_pdf(pdf_path, document_id)
    if not documents:
        print("PDF加载失败，程序退出")
        return
    
    # 添加文档到向量数据库
    metadata = {
        "source": "pdf",
        "language": "zh",
        "category": "resume"
    }
    
    success = retriever.add_documents_to_db(documents, document_id, metadata)
    if not success:
        print("添加文档到数据库失败，程序退出")
        return
    
    print("\n" + "="*80)
    print("=== 基于向量数据库的混合检索系统测试 ===")
    print("="*80)
    
    # 测试查询
    test_queries = [
        "张三的工作经验",
        "技术技能和编程语言", 
        "应聘的岗位和公司",
        "测试和开发经验"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print(f"{'='*60}")
        
        # 混合搜索
        results = retriever.hybrid_search_db(query, top_k_embedding=5, top_k_final=3)
        
        print(f"\n🎯 最终搜索结果:")
        for i, result in enumerate(results, 1):
            print(f"  结果{i}: 最终分数={result['final_score']:.4f}, "
                  f"Embedding相似度={result['embedding_similarity']:.4f}")
            print(f"    文档ID: {result['id']}")
            print(f"    内容: {result['document'][:100]}...")
            print(f"    元数据: {result['metadata']}")
    
    # 显示最终统计信息
    print(f"\n📊 最终数据库统计信息:")
    final_stats = retriever.get_database_stats()
    for key, value in final_stats.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    main() 