import fitz  # PyMuPDF
import numpy as np
from typing import List, Tuple, Dict
from test_qwen3_embedding import Qwen3Embedding
from test_qwen3_reranker import Qwen3Reranker
import torch
import re

class HybridPDFRetriever:
    def __init__(self, 
                 embedding_model_path: str = "models/Qwen3-Embedding-0.6B/Qwen/Qwen3-Embedding-0.6B",
                 reranker_model_path: str = "models/Qwen3-Reranker-0.6B/Qwen/Qwen3-Reranker-0.6B"):
        """
        初始化混合PDF检索器
        Args:
            embedding_model_path: Qwen3 Embedding模型路径
            reranker_model_path: Qwen3 Reranker模型路径
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
        
        self.documents = []
        self.embeddings = None
        self.chunk_size = 300
        
    def load_pdf(self, pdf_path: str) -> List[str]:
        """加载PDF文件并提取文本"""
        print(f"正在加载PDF文件: {pdf_path}")
        
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                full_text += f"第{page_num + 1}页: " + text + "\n"
            
            doc.close()
            
            self.documents = self._split_text(full_text)
            print(f"成功提取 {len(self.documents)} 个文本块")
            
            return self.documents
            
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
    
    def build_embeddings(self):
        """为所有文档构建向量表示"""
        if not self.documents:
            print("没有文档可以构建向量")
            return
            
        print("正在构建文档向量...")
        with torch.inference_mode():
            self.embeddings = self.embedding_model.encode(self.documents, is_query=False)
        print("文档向量构建完成")
    
    def hybrid_search(self, query: str, top_k_embedding: int = 10, top_k_final: int = 5) -> List[Tuple[str, float, int]]:
        """
        混合检索：Embedding粗筛 + Reranker精筛
        Args:
            query: 查询文本
            top_k_embedding: Embedding阶段返回的候选数量
            top_k_final: 最终返回的结果数量
        Returns:
            结果列表，每个元素包含(文档内容, 相关性分数, 文档索引)
        """
        if self.embeddings is None:
            print("请先调用 build_embeddings() 构建文档向量")
            return []
        
        print(f"正在进行混合检索: {query}")
        print("="*50)
        
        # 第一阶段：Embedding粗筛
        print("第一阶段：Embedding粗筛")
        with torch.inference_mode():
            query_embedding = self.embedding_model.encode([query], is_query=True)
        
        similarities = torch.mm(query_embedding, self.embeddings.T)
        similarities = similarities.squeeze().cpu().numpy()
        
        # 获取top-k候选
        top_indices = np.argsort(similarities)[::-1][:top_k_embedding]
        candidates = [(self.documents[idx], similarities[idx], idx) for idx in top_indices]
        
        print(f"Embedding阶段找到 {len(candidates)} 个候选文档:")
        for i, (doc, score, idx) in enumerate(candidates, 1):
            print(f"  候选{i}: 相似度={score:.4f}, 索引={idx}")
            print(f"    内容: {doc[:80]}...")
        
        # 第二阶段：Reranker精筛
        print(f"\n第二阶段：Reranker精筛")
        if len(candidates) > 0:
            # 构建查询-文档对
            pairs = [(query, doc) for doc, _, _ in candidates]
            
            # 使用Reranker计算相关性分数
            reranker_scores = self.reranker_model.compute_scores(pairs)
            
            # 组合结果
            reranked_results = []
            for i, (doc, embedding_score, idx) in enumerate(candidates):
                reranker_score = reranker_scores[i]
                reranked_results.append((doc, reranker_score, idx, embedding_score))
            
            # 按Reranker分数排序
            reranked_results.sort(key=lambda x: x[1], reverse=True)
            
            print(f"Reranker阶段重新排序结果:")
            for i, (doc, reranker_score, idx, embedding_score) in enumerate(reranked_results, 1):
                print(f"  排序{i}: Reranker分数={reranker_score:.4f}, Embedding分数={embedding_score:.4f}, 索引={idx}")
                print(f"    内容: {doc[:80]}...")
            
            # 返回最终结果
            final_results = [(doc, reranker_score, idx) for doc, reranker_score, idx, _ in reranked_results[:top_k_final]]
            return final_results
        
        return []
    
    def embedding_only_search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, int]]:
        """仅使用Embedding的搜索"""
        if self.embeddings is None:
            print("请先调用 build_embeddings() 构建文档向量")
            return []
        
        print(f"仅使用Embedding搜索: {query}")
        
        with torch.inference_mode():
            query_embedding = self.embedding_model.encode([query], is_query=True)
        
        similarities = torch.mm(query_embedding, self.embeddings.T)
        similarities = similarities.squeeze().cpu().numpy()
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            doc_content = self.documents[idx]
            results.append((doc_content, score, idx))
        
        return results
    
    def reranker_only_search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, int]]:
        """仅使用Reranker的搜索（对所有文档）"""
        print(f"仅使用Reranker搜索: {query}")
        
        if len(self.documents) == 0:
            print("没有文档可以搜索")
            return []
        
        # 构建所有查询-文档对
        pairs = [(query, doc) for doc in self.documents]
        
        # 使用Reranker计算相关性分数
        reranker_scores = self.reranker_model.compute_scores(pairs)
        
        # 组合结果并排序
        results = []
        for i, (doc, score) in enumerate(zip(self.documents, reranker_scores)):
            results.append((doc, score, i))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

def main():
    # 初始化检索器
    retriever = HybridPDFRetriever()
    
    # 加载PDF
    pdf_path = r"C:\Users\sanrome\Documents\三郎白底通用简历-zh.pdf"
    documents = retriever.load_pdf(pdf_path)
    if not documents:
        print("PDF加载失败，程序退出")
        return
    
    # 构建向量
    retriever.build_embeddings()
    
    print("\n" + "="*80)
    print("=== 混合检索系统测试 ===")
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
        
        # 1. 仅Embedding搜索
        print("\n1️⃣ 仅Embedding搜索:")
        embedding_results = retriever.embedding_only_search(query, top_k=3)
        for i, (doc, score, idx) in enumerate(embedding_results, 1):
            print(f"  结果{i}: 相似度={score:.4f}, 索引={idx}")
            print(f"    内容: {doc[:100]}...")
        
        # 2. 仅Reranker搜索
        print("\n2️⃣ 仅Reranker搜索:")
        reranker_results = retriever.reranker_only_search(query, top_k=3)
        for i, (doc, score, idx) in enumerate(reranker_results, 1):
            print(f"  结果{i}: 相关性={score:.4f}, 索引={idx}")
            print(f"    内容: {doc[:100]}...")
        
        # 3. 混合搜索
        print("\n3️⃣ 混合搜索 (Embedding + Reranker):")
        hybrid_results = retriever.hybrid_search(query, top_k_embedding=5, top_k_final=3)
        for i, (doc, score, idx) in enumerate(hybrid_results, 1):
            print(f"  结果{i}: 最终相关性={score:.4f}, 索引={idx}")
            print(f"    内容: {doc[:100]}...")

if __name__ == "__main__":
    main() 