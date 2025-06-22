#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向量数据库管理工具
提供批量文档管理、性能监控和数据库维护功能
"""

import os
import json
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import glob
from pathlib import Path
import pandas as pd
from hybrid_retrieval_db import HybridPDFRetrieverDB

class VectorDBManager:
    def __init__(self, db_path: str = "vector_db", collection_name: str = "documents"):
        """
        初始化向量数据库管理器
        Args:
            db_path: 向量数据库路径
            collection_name: 集合名称
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.retriever = HybridPDFRetrieverDB(db_path=db_path, collection_name=collection_name)
        
    def batch_add_pdfs(self, pdf_directory: str, metadata_template: Optional[Dict] = None) -> Dict:
        """
        批量添加PDF文档到向量数据库
        Args:
            pdf_directory: PDF文件目录
            metadata_template: 元数据模板
        Returns:
            批量操作结果
        """
        print(f"🔍 扫描PDF目录: {pdf_directory}")
        
        # 查找所有PDF文件
        pdf_files = glob.glob(os.path.join(pdf_directory, "*.pdf"))
        pdf_files.extend(glob.glob(os.path.join(pdf_directory, "**/*.pdf"), recursive=True))
        
        if not pdf_files:
            print("❌ 未找到PDF文件")
            return {"success": 0, "failed": 0, "files": []}
        
        print(f"📄 找到 {len(pdf_files)} 个PDF文件")
        
        results = {
            "success": 0,
            "failed": 0,
            "files": [],
            "start_time": datetime.now().isoformat()
        }
        
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] 处理文件: {os.path.basename(pdf_path)}")
            
            try:
                # 生成文档ID
                file_name = Path(pdf_path).stem
                document_id = f"{file_name}_{int(time.time())}"
                
                # 加载PDF
                documents = self.retriever.load_pdf(pdf_path, document_id)
                if not documents:
                    print(f"❌ PDF加载失败: {pdf_path}")
                    results["failed"] += 1
                    results["files"].append({
                        "path": pdf_path,
                        "status": "failed",
                        "error": "PDF loading failed"
                    })
                    continue
                
                # 准备元数据
                metadata = {
                    "source": "pdf",
                    "file_path": pdf_path,
                    "file_name": os.path.basename(pdf_path),
                    "file_size": os.path.getsize(pdf_path),
                    "upload_time": datetime.now().isoformat()
                }
                if metadata_template:
                    metadata.update(metadata_template)
                
                # 添加到数据库
                success = self.retriever.add_documents_to_db(documents, document_id, metadata)
                
                if success:
                    print(f"✅ 成功添加文档: {document_id}")
                    results["success"] += 1
                    results["files"].append({
                        "path": pdf_path,
                        "status": "success",
                        "document_id": document_id,
                        "chunks": len(documents)
                    })
                else:
                    print(f"❌ 添加文档失败: {document_id}")
                    results["failed"] += 1
                    results["files"].append({
                        "path": pdf_path,
                        "status": "failed",
                        "error": "Database insertion failed"
                    })
                    
            except Exception as e:
                print(f"❌ 处理文件异常: {e}")
                results["failed"] += 1
                results["files"].append({
                    "path": pdf_path,
                    "status": "failed",
                    "error": str(e)
                })
        
        results["end_time"] = datetime.now().isoformat()
        results["total_time"] = (datetime.fromisoformat(results["end_time"]) - 
                               datetime.fromisoformat(results["start_time"])).total_seconds()
        
        print(f"\n📊 批量操作完成:")
        print(f"   成功: {results['success']}")
        print(f"   失败: {results['failed']}")
        print(f"   总耗时: {results['total_time']:.2f}秒")
        
        return results
    
    def get_detailed_stats(self) -> Dict:
        """获取详细的数据库统计信息"""
        stats = self.retriever.get_database_stats()
        
        try:
            # 获取所有文档
            all_results = self.retriever.collection.get()
            
            # 分析文档分布
            document_stats = {}
            for metadata in all_results['metadatas']:
                if metadata and 'document_id' in metadata:
                    doc_id = metadata['document_id']
                    if doc_id not in document_stats:
                        document_stats[doc_id] = {
                            'chunks': 0,
                            'total_length': 0,
                            'upload_time': metadata.get('timestamp', ''),
                            'source': metadata.get('source', ''),
                            'category': metadata.get('category', '')
                        }
                    document_stats[doc_id]['chunks'] += 1
                    document_stats[doc_id]['total_length'] += metadata.get('chunk_length', 0)
            
            # 计算统计信息
            total_chunks = len(all_results['ids'])
            avg_chunk_length = sum(meta.get('chunk_length', 0) for meta in all_results['metadatas']) / total_chunks if total_chunks > 0 else 0
            
            detailed_stats = {
                **stats,
                'document_stats': document_stats,
                'avg_chunk_length': avg_chunk_length,
                'total_chunks': total_chunks,
                'database_size_mb': self._get_database_size(),
                'last_updated': datetime.now().isoformat()
            }
            
            return detailed_stats
            
        except Exception as e:
            print(f"❌ 获取详细统计信息失败: {e}")
            return stats
    
    def _get_database_size(self) -> float:
        """获取数据库文件大小（MB）"""
        try:
            total_size = 0
            for root, dirs, files in os.walk(self.db_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
            return total_size / (1024 * 1024)  # 转换为MB
        except:
            return 0.0
    
    def search_performance_test(self, queries: List[str], iterations: int = 3) -> Dict:
        """
        搜索性能测试
        Args:
            queries: 测试查询列表
            iterations: 测试迭代次数
        Returns:
            性能测试结果
        """
        print(f"🚀 开始搜索性能测试...")
        print(f"   查询数量: {len(queries)}")
        print(f"   迭代次数: {iterations}")
        
        results = {
            "queries": queries,
            "iterations": iterations,
            "embedding_times": [],
            "reranker_times": [],
            "total_times": [],
            "start_time": datetime.now().isoformat()
        }
        
        for iteration in range(iterations):
            print(f"\n📊 第 {iteration + 1} 轮测试:")
            
            for i, query in enumerate(queries, 1):
                print(f"   查询 {i}: {query}")
                
                # 测试Embedding搜索
                start_time = time.time()
                embedding_results = self.retriever.search_similar_documents(query, top_k=10)
                embedding_time = time.time() - start_time
                
                # 测试混合搜索
                start_time = time.time()
                hybrid_results = self.retriever.hybrid_search_db(query, top_k_embedding=10, top_k_final=5)
                total_time = time.time() - start_time
                
                reranker_time = total_time - embedding_time
                
                results["embedding_times"].append(embedding_time)
                results["reranker_times"].append(reranker_time)
                results["total_times"].append(total_time)
                
                print(f"     Embedding: {embedding_time:.3f}s, Reranker: {reranker_time:.3f}s, 总计: {total_time:.3f}s")
        
        # 计算统计信息
        results["avg_embedding_time"] = sum(results["embedding_times"]) / len(results["embedding_times"])
        results["avg_reranker_time"] = sum(results["reranker_times"]) / len(results["reranker_times"])
        results["avg_total_time"] = sum(results["total_times"]) / len(results["total_times"])
        results["end_time"] = datetime.now().isoformat()
        
        print(f"\n📈 性能测试结果:")
        print(f"   平均Embedding时间: {results['avg_embedding_time']:.3f}s")
        print(f"   平均Reranker时间: {results['avg_reranker_time']:.3f}s")
        print(f"   平均总时间: {results['avg_total_time']:.3f}s")
        
        return results
    
    def export_database_info(self, output_file: str = "database_export.json") -> bool:
        """
        导出数据库信息到JSON文件
        Args:
            output_file: 输出文件路径
        Returns:
            是否成功导出
        """
        try:
            print(f"📤 导出数据库信息到: {output_file}")
            
            # 获取详细统计信息
            stats = self.get_detailed_stats()
            
            # 获取所有文档内容
            all_results = self.retriever.collection.get()
            
            export_data = {
                "export_time": datetime.now().isoformat(),
                "database_stats": stats,
                "documents": []
            }
            
            # 整理文档信息
            for i in range(len(all_results['ids'])):
                doc_info = {
                    "id": all_results['ids'][i],
                    "document": all_results['documents'][i],
                    "metadata": all_results['metadatas'][i]
                }
                export_data["documents"].append(doc_info)
            
            # 写入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 成功导出 {len(export_data['documents'])} 个文档")
            return True
            
        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return False
    
    def cleanup_old_documents(self, days_old: int = 30) -> Dict:
        """
        清理旧文档
        Args:
            days_old: 删除多少天前的文档
        Returns:
            清理结果
        """
        print(f"🧹 清理 {days_old} 天前的文档...")
        
        try:
            # 获取所有文档
            all_results = self.retriever.collection.get()
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            documents_to_delete = []
            
            for i, metadata in enumerate(all_results['metadatas']):
                if metadata and 'timestamp' in metadata:
                    try:
                        doc_date = datetime.fromisoformat(metadata['timestamp'])
                        if doc_date < cutoff_date:
                            documents_to_delete.append(all_results['ids'][i])
                    except:
                        continue
            
            if not documents_to_delete:
                print("没有需要清理的旧文档")
                return {"deleted": 0, "total": len(all_results['ids'])}
            
            # 删除旧文档
            self.retriever.collection.delete(ids=documents_to_delete)
            
            print(f"✅ 成功删除 {len(documents_to_delete)} 个旧文档")
            
            return {
                "deleted": len(documents_to_delete),
                "total": len(all_results['ids']),
                "deleted_ids": documents_to_delete
            }
            
        except Exception as e:
            print(f"❌ 清理失败: {e}")
            return {"deleted": 0, "error": str(e)}
    
    def generate_report(self, output_file: str = "database_report.html") -> bool:
        """
        生成数据库报告
        Args:
            output_file: 输出HTML文件路径
        Returns:
            是否成功生成
        """
        try:
            print(f"📊 生成数据库报告: {output_file}")
            
            stats = self.get_detailed_stats()
            
            # 生成HTML报告
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>向量数据库报告</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                    .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                    .stat-card {{ background-color: #fff; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
                    .stat-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
                    .stat-label {{ color: #666; margin-top: 5px; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f8f9fa; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🔍 向量数据库报告</h1>
                    <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">{stats.get('total_chunks', 0)}</div>
                        <div class="stat-label">总文档块数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats.get('unique_documents', 0)}</div>
                        <div class="stat-label">唯一文档数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats.get('database_size_mb', 0):.2f} MB</div>
                        <div class="stat-label">数据库大小</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats.get('avg_chunk_length', 0):.0f}</div>
                        <div class="stat-label">平均块长度</div>
                    </div>
                </div>
                
                <h2>📋 文档详情</h2>
                <table>
                    <tr>
                        <th>文档ID</th>
                        <th>块数</th>
                        <th>总长度</th>
                        <th>来源</th>
                        <th>分类</th>
                    </tr>
            """
            
            for doc_id, doc_stats in stats.get('document_stats', {}).items():
                html_content += f"""
                    <tr>
                        <td>{doc_id}</td>
                        <td>{doc_stats['chunks']}</td>
                        <td>{doc_stats['total_length']}</td>
                        <td>{doc_stats['source']}</td>
                        <td>{doc_stats['category']}</td>
                    </tr>
                """
            
            html_content += """
                </table>
            </body>
            </html>
            """
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ 成功生成报告: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ 生成报告失败: {e}")
            return False

def main():
    """主函数 - 演示向量数据库管理功能"""
    
    print("=" * 80)
    print("🔧 向量数据库管理工具")
    print("=" * 80)
    
    # 初始化管理器
    manager = VectorDBManager()
    
    # 显示数据库统计信息
    print("\n📊 当前数据库状态:")
    stats = manager.get_detailed_stats()
    for key, value in stats.items():
        if key != 'document_stats':
            print(f"   {key}: {value}")
    
    # 性能测试
    print("\n🚀 性能测试:")
    test_queries = [
        "机器学习算法",
        "深度学习技术",
        "自然语言处理",
        "计算机视觉"
    ]
    
    performance_results = manager.search_performance_test(test_queries, iterations=2)
    
    # 生成报告
    print("\n📊 生成报告:")
    manager.generate_report("database_report.html")
    
    print("\n✅ 管理工具演示完成!")

if __name__ == "__main__":
    main() 