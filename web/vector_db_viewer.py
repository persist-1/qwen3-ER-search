#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向量数据库可视化软件
基于Streamlit的Web界面，用于查看和操作Chroma向量数据库
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import chromadb
from chromadb.config import Settings
import json
import os
from datetime import datetime
import numpy as np
from typing import Dict, List, Optional
import time

# 设置页面配置
st.set_page_config(
    page_title="向量数据库可视化工具",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加浏览器兼容性修复的CSS和JavaScript
st.markdown("""
<style>
/* 修复浏览器兼容性问题 */
@supports not (Object.hasOwn) {
    .stMarkdown {
        word-break: break-word;
    }
}

/* 确保所有文本区域都有适当的样式 */
.stTextArea textarea {
    font-family: monospace;
    font-size: 12px;
}
</style>

<script>
// 修复 Object.hasOwn 兼容性问题
if (!Object.hasOwn) {
    Object.hasOwn = function(obj, prop) {
        return Object.prototype.hasOwnProperty.call(obj, prop);
    };
}
</script>
""", unsafe_allow_html=True)

class VectorDBViewer:
    def __init__(self, db_path: str = "vector_db", collection_name: str = "documents"):
        """
        初始化向量数据库查看器
        Args:
            db_path: 数据库路径
            collection_name: 集合名称
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.connect_database()
    
    def connect_database(self):
        """连接到向量数据库"""
        try:
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_collection(name=self.collection_name)
            return True
        except Exception as e:
            st.error(f"连接数据库失败: {e}")
            return False
    
    def get_database_stats(self) -> Dict:
        """获取数据库统计信息"""
        try:
            count = self.collection.count()
            all_results = self.collection.get()
            
            # 统计文档ID
            document_ids = set()
            for metadata in all_results['metadatas']:
                if metadata and 'document_id' in metadata:
                    document_ids.add(metadata['document_id'])
            
            # 计算数据库大小
            db_size = 0
            for root, dirs, files in os.walk(self.db_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    db_size += os.path.getsize(file_path)
            
            stats = {
                'total_chunks': count,
                'unique_documents': len(document_ids),
                'document_ids': list(document_ids),
                'database_size_mb': db_size / (1024 * 1024),
                'collection_name': self.collection_name,
                'database_path': self.db_path
            }
            
            return stats
        except Exception as e:
            st.error(f"获取统计信息失败: {e}")
            return {}
    
    def get_all_documents(self) -> pd.DataFrame:
        """获取所有文档数据"""
        try:
            results = self.collection.get()
            
            # 创建DataFrame
            data = []
            for i in range(len(results['ids'])):
                metadata = results['metadatas'][i] or {}
                data.append({
                    'ID': results['ids'][i],
                    'Document': results['documents'][i],
                    'Document_ID': metadata.get('document_id', ''),
                    'Chunk_Index': metadata.get('chunk_index', ''),
                    'Chunk_Length': metadata.get('chunk_length', ''),
                    'Source': metadata.get('source', ''),
                    'Category': metadata.get('category', ''),
                    'Language': metadata.get('language', ''),
                    'Timestamp': metadata.get('timestamp', ''),
                    'File_Name': metadata.get('file_name', ''),
                    'File_Size': metadata.get('file_size', '')
                })
            
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"获取文档数据失败: {e}")
            return pd.DataFrame()
    
    def search_documents(self, query: str, top_k: int = 10) -> List[Dict]:
        """搜索文档"""
        try:
            # 这里需要加载embedding模型来生成查询向量
            # 为了简化，我们使用文本搜索
            all_docs = self.get_all_documents()
            
            # 简单的文本搜索
            results = []
            for _, row in all_docs.iterrows():
                if query.lower() in row['Document'].lower():
                    results.append({
                        'ID': row['ID'],
                        'Document': row['Document'],
                        'Document_ID': row['Document_ID'],
                        'Chunk_Index': row['Chunk_Index'],
                        'Source': row['Source'],
                        'Category': row['Category']
                    })
            
            return results[:top_k]
        except Exception as e:
            st.error(f"搜索失败: {e}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """删除文档"""
        try:
            # 查找所有属于该文档的块
            results = self.collection.get(where={"document_id": document_id})
            
            if not results['ids']:
                st.warning(f"未找到文档ID为 {document_id} 的文档")
                return False
            
            # 删除这些块
            self.collection.delete(ids=results['ids'])
            st.success(f"成功删除文档 {document_id} 的 {len(results['ids'])} 个块")
            return True
            
        except Exception as e:
            st.error(f"删除文档失败: {e}")
            return False
    
    def add_document(self, document_text: str, document_id: str, metadata: Dict = None) -> bool:
        """添加文档到数据库"""
        try:
            if not metadata:
                metadata = {
                    "source": "web_upload",
                    "category": "general",
                    "language": "zh",
                    "timestamp": datetime.now().isoformat(),
                    "file_name": f"{document_id}.txt"
                }
            
            # 分割文本为块
            chunks = self._split_text(document_text)
            
            # 使用Qwen3-Embedding模型生成1024维向量
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))
            
            try:
                from test_qwen3_embedding import Qwen3Embedding
                import torch
                
                # 初始化embedding模型
                embedding_model = Qwen3Embedding("models/Qwen3-Embedding-0.6B/Qwen/Qwen3-Embedding-0.6B")
                
                # 生成向量
                with torch.inference_mode():
                    embeddings = embedding_model.encode(chunks, is_query=False)
                
                # 添加到数据库
                self.collection.add(
                    documents=chunks,
                    embeddings=embeddings.cpu().numpy().tolist(),
                    metadatas=[{
                        **metadata,
                        "document_id": document_id,
                        "chunk_index": i,
                        "chunk_length": len(chunk)
                    } for i, chunk in enumerate(chunks)],
                    ids=[f"{document_id}_chunk_{i}" for i in range(len(chunks))]
                )
                
                return True
                
            except ImportError:
                # 如果无法导入Qwen3模型，使用备用方案
                st.warning("无法加载Qwen3-Embedding模型，使用备用方案")
                return self._add_document_fallback(chunks, document_id, metadata)
                
        except Exception as e:
            st.error(f"添加文档失败: {e}")
            return False
    
    def _add_document_fallback(self, chunks: List[str], document_id: str, metadata: Dict) -> bool:
        """备用添加方案：创建新的collection"""
        try:
            # 创建一个新的collection用于测试
            test_collection_name = f"documents_{int(time.time())}"
            test_collection = self.client.create_collection(name=test_collection_name)
            
            # 添加到新collection
            test_collection.add(
                documents=chunks,
                metadatas=[{
                    **metadata,
                    "document_id": document_id,
                    "chunk_index": i,
                    "chunk_length": len(chunk)
                } for i, chunk in enumerate(chunks)],
                ids=[f"{document_id}_chunk_{i}" for i in range(len(chunks))]
            )
            
            st.success(f"文档已添加到新collection: {test_collection_name}")
            return True
            
        except Exception as e:
            st.error(f"备用方案也失败: {e}")
            return False
    
    def _split_text(self, text: str, chunk_size: int = 300) -> List[str]:
        """将文本分割成块"""
        import re
        sentences = re.split(r'[。！？；\n]', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence + "。"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + "。"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    def get_document_info(self, document_id: str) -> Optional[Dict]:
        """获取文档详细信息"""
        try:
            results = self.collection.get(where={"document_id": document_id})
            
            if not results['ids']:
                return None
            
            total_length = 0
            for metadata in results['metadatas']:
                if metadata:
                    total_length += metadata.get('chunk_length', 0)
            
            return {
                'chunks': len(results['ids']),
                'total_length': total_length,
                'first_chunk': results['documents'][0][:100] + "..." if results['documents'] else ""
            }
        except Exception as e:
            st.error(f"获取文档信息失败: {e}")
            return None

def main():
    st.title("🗄️ 向量数据库可视化工具")
    st.markdown("---")
    
    # 初始化session_state
    if 'refresh_trigger' not in st.session_state:
        st.session_state.refresh_trigger = 0
    
    # 侧边栏配置
    st.sidebar.header("⚙️ 配置")
    db_path = st.sidebar.text_input("数据库路径", value="vector_db")
    collection_name = st.sidebar.text_input("集合名称", value="documents")
    
    # 初始化查看器
    viewer = VectorDBViewer(db_path, collection_name)
    
    if viewer.collection is None:
        st.error("无法连接到数据库，请检查配置")
        return
    
    # 获取数据库统计信息
    stats = viewer.get_database_stats()
    
    # 主界面
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 概览", 
        "📋 文档列表", 
        "🔍 搜索", 
        "📈 分析", 
        "⚙️ 管理"
    ])
    
    with tab1:
        st.header("📊 数据库概览")
        
        # 统计卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="总文档块数",
                value=stats.get('total_chunks', 0),
                help="数据库中存储的文档块总数"
            )
        
        with col2:
            st.metric(
                label="唯一文档数",
                value=stats.get('unique_documents', 0),
                help="不同的文档数量"
            )
        
        with col3:
            st.metric(
                label="数据库大小",
                value=f"{stats.get('database_size_mb', 0):.2f} MB",
                help="数据库文件占用的磁盘空间"
            )
        
        with col4:
            st.metric(
                label="集合名称",
                value=stats.get('collection_name', ''),
                help="当前连接的集合名称"
            )
        
        # 文档ID列表
        st.subheader("📄 文档列表")
        if stats.get('document_ids'):
            for doc_id in stats['document_ids']:
                st.write(f"• {doc_id}")
        else:
            st.info("暂无文档")
        
        # 数据库信息
        st.subheader("ℹ️ 数据库信息")
        info_df = pd.DataFrame([
            {"属性": "数据库路径", "值": stats.get('database_path', '')},
            {"属性": "集合名称", "值": stats.get('collection_name', '')},
            {"属性": "总块数", "值": stats.get('total_chunks', 0)},
            {"属性": "唯一文档数", "值": stats.get('unique_documents', 0)},
            {"属性": "数据库大小", "值": f"{stats.get('database_size_mb', 0):.2f} MB"},
        ])
        st.dataframe(info_df, use_container_width=True)
    
    with tab2:
        st.header("📋 文档列表")
        
        # 获取所有文档
        df = viewer.get_all_documents()
        
        if not df.empty:
            # 搜索框
            search_term = st.text_input("🔍 搜索文档内容", placeholder="输入关键词...")
            if search_term:
                df = df[df['Document'].str.contains(search_term, case=False, na=False)]
            
            # 显示文档数量
            st.info(f"显示 {len(df)} 个文档块")
            
            # 分页显示
            page_size = st.selectbox("每页显示数量", [10, 25, 50, 100])
            total_pages = (len(df) + page_size - 1) // page_size
            
            if total_pages > 1:
                page = st.selectbox("选择页面", range(1, total_pages + 1))
                start_idx = (page - 1) * page_size
                end_idx = start_idx + page_size
                page_df = df.iloc[start_idx:end_idx]
            else:
                page_df = df
            
            # 显示文档
            for idx, row in page_df.iterrows():
                with st.expander(f"📄 {row['ID']} - {row['Document'][:100]}..."):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write("**文档内容:**")
                        st.text_area("文档内容", value=row['Document'], height=150, key=f"doc_{idx}", label_visibility="collapsed")
                    
                    with col2:
                        st.write("**元数据:**")
                        metadata = {
                            "文档ID": row['Document_ID'],
                            "块索引": row['Chunk_Index'],
                            "块长度": row['Chunk_Length'],
                            "来源": row['Source'],
                            "分类": row['Category'],
                            "语言": row['Language'],
                            "时间戳": row['Timestamp'],
                            "文件名": row['File_Name']
                        }
                        
                        for key, value in metadata.items():
                            if pd.notna(value) and value != '':
                                st.write(f"**{key}:** {value}")
        else:
            st.warning("暂无文档数据")
    
    with tab3:
        st.header("🔍 搜索文档")
        
        # 搜索选项
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input("输入搜索关键词", placeholder="例如：机器学习、工作经验...")
        
        with col2:
            top_k = st.number_input("返回结果数量", min_value=1, max_value=50, value=10)
        
        if st.button("🔍 搜索", type="primary"):
            if search_query:
                with st.spinner("正在搜索..."):
                    results = viewer.search_documents(search_query, top_k)
                
                if results:
                    st.success(f"找到 {len(results)} 个相关文档")
                    
                    for i, result in enumerate(results, 1):
                        with st.expander(f"结果 {i}: {result['ID']}"):
                            st.write("**文档内容:**")
                            st.text_area("搜索结果", value=result['Document'], height=100, key=f"search_{i}", label_visibility="collapsed")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write(f"**文档ID:** {result['Document_ID']}")
                            with col2:
                                st.write(f"**块索引:** {result['Chunk_Index']}")
                            with col3:
                                st.write(f"**分类:** {result['Category']}")
                else:
                    st.info("未找到相关文档")
            else:
                st.warning("请输入搜索关键词")
    
    with tab4:
        st.header("📈 数据分析")
        
        df = viewer.get_all_documents()
        
        if not df.empty:
            # 文档分布分析
            st.subheader("📊 文档分布")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 按来源分布
                if 'Source' in df.columns and not df['Source'].isna().all():
                    source_counts = df['Source'].value_counts()
                    fig_source = px.pie(
                        values=source_counts.values,
                        names=source_counts.index,
                        title="按来源分布"
                    )
                    st.plotly_chart(fig_source, use_container_width=True)
            
            with col2:
                # 按分类分布
                if 'Category' in df.columns and not df['Category'].isna().all():
                    category_counts = df['Category'].value_counts()
                    fig_category = px.pie(
                        values=category_counts.values,
                        names=category_counts.index,
                        title="按分类分布"
                    )
                    st.plotly_chart(fig_category, use_container_width=True)
            
            # 块长度分布
            st.subheader("📏 块长度分布")
            if 'Chunk_Length' in df.columns and not df['Chunk_Length'].isna().all():
                chunk_lengths = pd.to_numeric(df['Chunk_Length'], errors='coerce')
                chunk_lengths = chunk_lengths.dropna()
                
                if len(chunk_lengths) > 0:
                    fig_length = px.histogram(
                        x=chunk_lengths,
                        title="文档块长度分布",
                        labels={'x': '块长度', 'y': '数量'}
                    )
                    st.plotly_chart(fig_length, use_container_width=True)
                    
                    # 统计信息
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("平均长度", f"{chunk_lengths.mean():.1f}")
                    with col2:
                        st.metric("最大长度", f"{chunk_lengths.max():.0f}")
                    with col3:
                        st.metric("最小长度", f"{chunk_lengths.min():.0f}")
                    with col4:
                        st.metric("标准差", f"{chunk_lengths.std():.1f}")
            
            # 时间分布
            st.subheader("⏰ 时间分布")
            if 'Timestamp' in df.columns and not df['Timestamp'].isna().all():
                # 解析时间戳
                timestamps = []
                for ts in df['Timestamp']:
                    try:
                        if pd.notna(ts) and ts != '':
                            timestamps.append(pd.to_datetime(ts))
                    except:
                        continue
                
                if timestamps:
                    timestamps = pd.Series(timestamps)
                    fig_time = px.histogram(
                        x=timestamps,
                        title="文档添加时间分布",
                        labels={'x': '时间', 'y': '数量'}
                    )
                    st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.warning("暂无数据可分析")
    
    with tab5:
        st.header("⚙️ 数据库管理")
        
        # 新增功能
        st.subheader("📝 新增文档")
        
        add_method = st.radio("选择添加方式", ["文本输入", "文件上传"])
        
        if add_method == "文本输入":
            col1, col2 = st.columns([2, 1])
            
            with col1:
                document_text = st.text_area("文档内容", height=200, placeholder="请输入要添加的文档内容...")
            
            with col2:
                document_id = st.text_input("文档ID", placeholder="例如：doc_001")
                category = st.selectbox("分类", ["general", "technical", "business", "academic", "other"])
                language = st.selectbox("语言", ["zh", "en", "other"])
                
                if st.button("📝 添加文档", type="primary"):
                    if document_text and document_id:
                        metadata = {
                            "source": "web_text",
                            "category": category,
                            "language": language,
                            "timestamp": datetime.now().isoformat(),
                            "file_name": f"{document_id}.txt"
                        }
                        
                        with st.spinner("正在添加文档..."):
                            if viewer.add_document(document_text, document_id, metadata):
                                st.success(f"✅ 文档 {document_id} 添加成功！")
                                # 触发刷新
                                st.session_state.refresh_trigger += 1
                                st.rerun()
                    else:
                        st.warning("请填写文档内容和文档ID")
        
        else:  # 文件上传
            uploaded_file = st.file_uploader("选择文件", type=['txt', 'pdf'], help="支持txt和pdf文件")
            
            if uploaded_file is not None:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**文件名:** {uploaded_file.name}")
                    st.write(f"**文件大小:** {uploaded_file.size} bytes")
                    
                    # 读取文件内容
                    if uploaded_file.type == "text/plain":
                        content = uploaded_file.read().decode('utf-8')
                        st.text_area("文件内容预览", content[:500] + "..." if len(content) > 500 else content, height=150)
                    else:
                        st.info("PDF文件预览功能开发中...")
                        content = "PDF文件内容"
                
                with col2:
                    document_id = st.text_input("文档ID", value=uploaded_file.name.split('.')[0])
                    category = st.selectbox("分类", ["general", "technical", "business", "academic", "other"])
                    language = st.selectbox("语言", ["zh", "en", "other"])
                    
                    if st.button("📁 上传文档", type="primary"):
                        if document_id:
                            metadata = {
                                "source": "web_upload",
                                "category": category,
                                "language": language,
                                "timestamp": datetime.now().isoformat(),
                                "file_name": uploaded_file.name,
                                "file_size": uploaded_file.size
                            }
                            
                            if uploaded_file.type == "text/plain":
                                with st.spinner("正在上传文档..."):
                                    if viewer.add_document(content, document_id, metadata):
                                        st.success(f"✅ 文档 {document_id} 上传成功！")
                                        # 触发刷新
                                        st.session_state.refresh_trigger += 1
                                        st.rerun()
                            else:
                                st.info("PDF文件处理功能开发中，请使用文本文件")
                        else:
                            st.warning("请填写文档ID")
        
        st.markdown("---")
        
        # 导出功能
        st.subheader("📤 导出数据")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("导出为JSON"):
                try:
                    df = viewer.get_all_documents()
                    if not df.empty:
                        # 转换为JSON格式
                        json_data = df.to_dict('records')
                        
                        # 添加统计信息
                        export_data = {
                            "export_time": datetime.now().isoformat(),
                            "database_stats": stats,
                            "documents": json_data
                        }
                        
                        # 保存文件
                        filename = f"database_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(export_data, f, ensure_ascii=False, indent=2)
                        
                        st.success(f"数据已导出到 {filename}")
                        
                        # 提供下载链接
                        with open(filename, 'r', encoding='utf-8') as f:
                            st.download_button(
                                label="📥 下载JSON文件",
                                data=f.read(),
                                file_name=filename,
                                mime="application/json"
                            )
                    else:
                        st.warning("暂无数据可导出")
                except Exception as e:
                    st.error(f"导出失败: {e}")
        
        with col2:
            if st.button("导出为CSV"):
                try:
                    df = viewer.get_all_documents()
                    if not df.empty:
                        filename = f"database_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                        df.to_csv(filename, index=False, encoding='utf-8-sig')
                        st.success(f"数据已导出到 {filename}")
                        
                        # 提供下载链接
                        with open(filename, 'r', encoding='utf-8-sig') as f:
                            st.download_button(
                                label="📥 下载CSV文件",
                                data=f.read(),
                                file_name=filename,
                                mime="text/csv"
                            )
                    else:
                        st.warning("暂无数据可导出")
                except Exception as e:
                    st.error(f"导出失败: {e}")
        
        # 删除功能
        st.subheader("🗑️ 删除文档")
        
        # 初始化删除相关的session_state
        if 'delete_confirmed' not in st.session_state:
            st.session_state.delete_confirmed = False
        if 'doc_to_delete' not in st.session_state:
            st.session_state.doc_to_delete = None
        if 'delete_message' not in st.session_state:
            st.session_state.delete_message = ""
        
        if stats.get('document_ids'):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                doc_to_delete = st.selectbox("选择要删除的文档", stats['document_ids'], key="delete_select")
                
                # 显示要删除的文档信息
                if doc_to_delete:
                    doc_info = viewer.get_document_info(doc_to_delete)
                    if doc_info:
                        st.info(f"**文档信息:** {doc_info['chunks']} 个块，总长度 {doc_info['total_length']} 字符")
                        st.warning(f"⚠️ 删除后将无法恢复，请谨慎操作！")
            
            with col2:
                # 确认删除复选框
                confirm_delete = st.checkbox("我确认要删除这个文档", key="confirm_delete_checkbox")
                
                # 删除按钮
                delete_button = st.button("🗑️ 删除文档", type="secondary", help="删除选中的文档", key="delete_btn")
                
                # 显示删除消息
                if st.session_state.delete_message:
                    if "成功" in st.session_state.delete_message:
                        st.success(st.session_state.delete_message)
                    else:
                        st.error(st.session_state.delete_message)
                    # 清除消息
                    st.session_state.delete_message = ""
                
                # 处理删除操作
                if delete_button:
                    if confirm_delete and doc_to_delete:
                        with st.spinner("正在删除..."):
                            try:
                                if viewer.delete_document(doc_to_delete):
                                    st.session_state.delete_message = f"✅ 文档 {doc_to_delete} 已成功删除"
                                    # 重置确认状态
                                    st.session_state.delete_confirmed = False
                                    # 触发刷新
                                    st.session_state.refresh_trigger += 1
                                    st.rerun()
                                else:
                                    st.session_state.delete_message = f"❌ 删除文档 {doc_to_delete} 失败"
                                    st.rerun()
                            except Exception as e:
                                st.session_state.delete_message = f"❌ 删除过程中发生错误: {str(e)}"
                                st.rerun()
                    else:
                        if not confirm_delete:
                            st.warning("⚠️ 请先确认删除操作")
                        else:
                            st.warning("⚠️ 请选择要删除的文档")
        else:
            st.info("暂无文档可删除")
        
        # 数据库信息
        st.subheader("ℹ️ 数据库信息")
        st.json(stats)

if __name__ == "__main__":
    main() 