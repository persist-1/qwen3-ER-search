import fitz  # PyMuPDF
import numpy as np
from typing import List, Tuple, Dict
from .test_qwen3_embedding import Qwen3Embedding
import torch
import re

class PDFRetriever:
    def __init__(self, model_path: str = "models/Qwen3-Embedding-0.6B/Qwen/Qwen3-Embedding-0.6B"):
        """
        初始化PDF检索器
        Args:
            model_path: Qwen3 Embedding模型路径
        """
        self.embedding_model = Qwen3Embedding(model_path)
        self.documents = []
        self.embeddings = None
        self.chunk_size = 200  # 文本块大小
        self.overlap = 50      # 重叠大小
        
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
                full_text += text + "\n"
            
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
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, int]]:
        """
        搜索相关文档
        Args:
            query: 查询文本
            top_k: 返回前k个结果
        Returns:
            结果列表，每个元素包含(文档内容, 相似度分数, 文档索引)
        """
        if self.embeddings is None:
            print("请先调用 build_embeddings() 构建文档向量")
            return []
        
        print(f"正在搜索: {query}")
        
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
    
    def search_exact_text(self, target_text: str) -> List[Tuple[str, int]]:
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
    retriever = PDFRetriever()
    
    # 示例用法
    print("=== PDF文本检索系统 ===")
    print("请提供PDF文件路径:")
    pdf_path = input().strip()
    
    if not pdf_path:
        print("使用示例PDF路径...")
        pdf_path = "example.pdf"  # 您可以替换为实际的PDF路径
    
    # 加载PDF
    documents = retriever.load_pdf(pdf_path)
    if not documents:
        print("PDF加载失败，程序退出")
        return
    
    # 构建向量
    retriever.build_embeddings()
    
    # 交互式搜索
    while True:
        print("\n=== 搜索选项 ===")
        print("1. 语义搜索")
        print("2. 精确文本搜索")
        print("3. 退出")
        
        choice = input("请选择 (1-3): ").strip()
        
        if choice == "1":
            query = input("请输入搜索查询: ").strip()
            if query:
                results = retriever.search(query, top_k=3)
                print(f"\n找到 {len(results)} 个相关结果:")
                for i, (doc, score, idx) in enumerate(results, 1):
                    print(f"\n--- 结果 {i} (相似度: {score:.4f}) ---")
                    print(f"文档索引: {idx}")
                    print(f"内容: {doc[:200]}...")
        
        elif choice == "2":
            target_text = input("请输入要查找的精确文本: ").strip()
            if target_text:
                results = retriever.search_exact_text(target_text)
                print(f"\n找到 {len(results)} 个包含目标文本的文档:")
                for i, (doc, idx) in enumerate(results, 1):
                    print(f"\n--- 结果 {i} ---")
                    print(f"文档索引: {idx}")
                    print(f"内容: {doc[:200]}...")
        
        elif choice == "3":
            print("退出程序")
            break
        
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main() 