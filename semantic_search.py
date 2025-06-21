import fitz  # PyMuPDF
import numpy as np
from typing import List, Tuple, Dict
from test_qwen3_embedding import Qwen3Embedding
import torch
import re

class SemanticPDFRetriever:
    def __init__(self, model_path: str = "models/Qwen3-Embedding-0.6B/Qwen/Qwen3-Embedding-0.6B"):
        """
        初始化语义PDF检索器
        Args:
            model_path: Qwen3 Embedding模型路径
        """
        print("正在加载Qwen3 Embedding模型...")
        self.embedding_model = Qwen3Embedding(model_path)
        self.documents = []
        self.embeddings = None
        self.chunk_size = 300  # 文本块大小
        print("模型加载完成！")
        
    def load_pdf(self, pdf_path: str) -> List[str]:
        """
        加载PDF文件并提取文本
        Args:
            pdf_path: PDF文件路径
        Returns:
            提取的文本块列表
        """
        print(f"正在加载PDF文件: {pdf_path}")
        
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                full_text += f"第{page_num + 1}页: " + text + "\n"
            
            doc.close()
            
            # 分块处理文本
            self.documents = self._split_text(full_text)
            print(f"成功提取 {len(self.documents)} 个文本块")
            
            return self.documents
            
        except Exception as e:
            print(f"加载PDF文件失败: {e}")
            return []
    
    def _split_text(self, text: str) -> List[str]:
        """
        将文本分割成小块
        Args:
            text: 完整文本
        Returns:
            文本块列表
        """
        # 按句子分割
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
        """
        为所有文档构建向量表示
        """
        if not self.documents:
            print("没有文档可以构建向量")
            return
            
        print("正在构建文档向量...")
        with torch.inference_mode():
            self.embeddings = self.embedding_model.encode(self.documents, is_query=False)
        print("文档向量构建完成")
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, int]]:
        """
        语义搜索相关文档
        Args:
            query: 查询文本
            top_k: 返回前k个结果
        Returns:
            结果列表，每个元素包含(文档内容, 相似度分数, 文档索引)
        """
        if self.embeddings is None:
            print("请先调用 build_embeddings() 构建文档向量")
            return []
        
        print(f"正在进行语义搜索: {query}")
        
        # 编码查询
        with torch.inference_mode():
            query_embedding = self.embedding_model.encode([query], is_query=True)
        
        # 计算相似度
        similarities = torch.mm(query_embedding, self.embeddings.T)
        similarities = similarities.squeeze().cpu().numpy()
        
        # 获取top-k结果
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            doc_content = self.documents[idx]
            results.append((doc_content, score, idx))
        
        return results
    
    def exact_search(self, target_text: str) -> List[Tuple[str, int]]:
        """
        精确文本搜索
        Args:
            target_text: 目标文本
        Returns:
            包含目标文本的文档列表
        """
        results = []
        for i, doc in enumerate(self.documents):
            if target_text.lower() in doc.lower():
                results.append((doc, i))
        return results

def main():
    # 初始化检索器
    retriever = SemanticPDFRetriever()
    
    # 加载PDF
    pdf_path = r"C:\Users\sanrome\Documents\三郎白底通用简历-zh.pdf"
    documents = retriever.load_pdf(pdf_path)
    if not documents:
        print("PDF加载失败，程序退出")
        return
    
    # 构建向量
    retriever.build_embeddings()
    
    print("\n" + "="*60)
    print("=== 语义搜索测试 ===")
    print("="*60)
    
    # 测试1: 精确姓名搜索
    print("\n1. 精确搜索 '张三':")
    exact_results = retriever.exact_search("张三")
    if exact_results:
        print("✅ 精确匹配找到结果:")
        for doc, idx in exact_results:
            print(f"  文档{idx}: {doc[:100]}...")
    else:
        print("❌ 精确匹配未找到")
    
    # 测试2: 语义搜索姓名
    print("\n2. 语义搜索 '张三':")
    semantic_results = retriever.semantic_search("张三", top_k=3)
    print(f"找到 {len(semantic_results)} 个语义相关结果:")
    for i, (doc, score, idx) in enumerate(semantic_results, 1):
        print(f"\n--- 结果 {i} (相似度: {score:.4f}) ---")
        print(f"文档索引: {idx}")
        print(f"内容: {doc[:150]}...")
    
    # 测试3: 语义搜索相关概念
    print("\n3. 语义搜索 '应聘者':")
    semantic_results = retriever.semantic_search("应聘者", top_k=3)
    print(f"找到 {len(semantic_results)} 个语义相关结果:")
    for i, (doc, score, idx) in enumerate(semantic_results, 1):
        print(f"\n--- 结果 {i} (相似度: {score:.4f}) ---")
        print(f"文档索引: {idx}")
        print(f"内容: {doc[:150]}...")
    
    # 测试4: 语义搜索工作经历
    print("\n4. 语义搜索 '工作经验':")
    semantic_results = retriever.semantic_search("工作经验", top_k=3)
    print(f"找到 {len(semantic_results)} 个语义相关结果:")
    for i, (doc, score, idx) in enumerate(semantic_results, 1):
        print(f"\n--- 结果 {i} (相似度: {score:.4f}) ---")
        print(f"文档索引: {idx}")
        print(f"内容: {doc[:150]}...")
    
    # 测试5: 语义搜索技术技能
    print("\n5. 语义搜索 '技术技能':")
    semantic_results = retriever.semantic_search("技术技能", top_k=3)
    print(f"找到 {len(semantic_results)} 个语义相关结果:")
    for i, (doc, score, idx) in enumerate(semantic_results, 1):
        print(f"\n--- 结果 {i} (相似度: {score:.4f}) ---")
        print(f"文档索引: {idx}")
        print(f"内容: {doc[:150]}...")

if __name__ == "__main__":
    main() 