# Qwen3-ER-Search 检索系统

基于Qwen3模型的智能文档检索系统，支持语义搜索和精准重排序。

## 🚀 功能特性

- **语义检索**: 使用Qwen3-Embedding模型进行语义相似度搜索
- **精准重排序**: 使用Qwen3-Reranker模型对搜索结果进行精确排序
- **混合检索**: 结合Embedding和Reranker的两阶段检索策略
- **PDF支持**: 支持PDF文档的文本提取和检索
- **向量数据库**: 支持Chroma向量数据库持久化存储
- **Web可视化**: 提供Streamlit Web界面进行数据库管理和可视化
- **API服务**: 提供Ray Serve API服务
- **多平台**: 支持Windows、Linux、MacOS

## 📁 项目结构

```
qwen3-er-search/
├── src/                           # 源代码目录
│   ├── core/                      # 核心功能模块
│   │   ├── test_qwen3_embedding.py    # Embedding模型测试
│   │   ├── test_qwen3_reranker.py     # Reranker模型测试
│   │   ├── hybrid_retrieval.py        # 混合检索系统
│   │   ├── hybrid_retrieval_db.py     # 带数据库的混合检索
│   │   ├── semantic_search.py         # 语义搜索示例
│   │   ├── search_name.py             # 姓名精确搜索
│   │   └── pdf_retrieval.py           # PDF检索工具
│   ├── api/                       # API服务模块
│   │   ├── ray_qwen3.py              # Ray Serve API服务
│   │   └── embeeding4openai.py       # OpenAI兼容接口
│   ├── tools/                     # 工具模块
│   │   └── vector_db_manager.py      # 向量数据库管理工具
│   └── utils/                     # 工具函数模块
├── web/                          # Web界面模块
│   └── vector_db_viewer.py          # 向量数据库可视化工具
├── scripts/                      # 脚本文件
│   ├── download_models.ps1          # 模型下载脚本（PowerShell）
│   ├── download_models.bat          # 模型下载脚本（Windows CMD）
│   ├── download_models.sh           # 模型下载脚本（Linux/Mac）
│   ├── start_viewer.bat             # 启动可视化工具（Windows）
│   └── start_viewer.ps1             # 启动可视化工具（PowerShell）
├── docs/                         # 文档目录
│   ├── README.md                    # 详细说明文档
│   ├── ray_config_guide.md          # Ray配置指南
│   ├── 向量数据库可视化软件使用说明.md  # 可视化工具使用说明
│   └── database_report.html         # 数据库报告
├── examples/                      # 示例文件
│   └── client.ipynb                # Jupyter客户端示例
├── tests/                         # 测试文件
│   ├── test_ray_api.py             # API测试
│   ├── test_add_document.py        # 文档添加测试
│   ├── test_add_document_simple.py # 简化文档添加测试
│   ├── test_db_operations.py       # 数据库操作测试
│   └── simple_test.py              # 基础功能测试
├── models/                        # 模型文件目录（不包含在Git中）
├── vector_db/                     # 向量数据库目录
├── requirements.txt               # 项目依赖
└── .gitignore                     # Git忽略文件
```

## 🛠️ 安装步骤

### 1. 克隆项目
```bash
git clone https://github.com/SanroZhang/qwen3-ER-search.git
cd qwen3-ER-search
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 下载模型
```bash
# Windows PowerShell
.\scripts\download_models.ps1

# Windows CMD
scripts\download_models.bat

# Linux/Mac
chmod +x scripts/download_models.sh
./scripts/download_models.sh
```

## 🎯 使用示例

### 基础测试
```bash
# 测试Embedding模型
python src/core/test_qwen3_embedding.py

# 测试Reranker模型
python src/core/test_qwen3_reranker.py
```

### 语义搜索
```bash
# 运行语义搜索示例
python src/core/semantic_search.py
```

### 混合检索
```bash
# 运行混合检索系统
python src/core/hybrid_retrieval.py

# 运行带数据库的混合检索
python src/core/hybrid_retrieval_db.py
```

### 向量数据库管理
```bash
# 运行数据库管理工具
python src/tools/vector_db_manager.py
```

### Web可视化
```bash
# 启动可视化工具
python web/vector_db_viewer.py

# 或使用脚本启动
.\scripts\start_viewer.bat
```

### API服务
```bash
# 启动Ray Serve API服务
python src/api/ray_qwen3.py
```

## 🔧 模型说明

### Qwen3-Embedding-0.6B
- **功能**: 文本向量化，计算语义相似度
- **特点**: 速度快，适合粗筛阶段
- **应用**: 从大量文档中快速筛选候选

### Qwen3-Reranker-0.6B
- **功能**: 文档相关性重排序
- **特点**: 精度高，适合精筛阶段
- **应用**: 对候选文档进行精确排序

## 📊 检索策略对比

| 方法 | 速度 | 精度 | 适用场景 |
|------|------|------|----------|
| **仅Embedding** | ⚡ 快 | 🎯 中等 | 大规模文档粗筛 |
| **仅Reranker** | 🐌 慢 | 🎯 高 | 小规模文档精筛 |
| **混合检索** | ⚡ 中等 | 🎯 高 | 生产环境推荐 |

## 🌐 API服务

### 启动Ray Serve服务
```bash
python src/api/ray_qwen3.py
```

### API接口
- `POST /embedding/api`: 文本向量化
- `POST /reranker/api`: 文档重排序
- `POST /v1/embeddings`: OpenAI兼容接口

## 📝 配置说明

### 模型路径配置
```python
# 默认模型路径
embedding_model_path = "models/Qwen3-Embedding-0.6B/Qwen/Qwen3-Embedding-0.6B"
reranker_model_path = "models/Qwen3-Reranker-0.6B/Qwen/Qwen3-Reranker-0.6B"
```

### 检索参数
```python
# 混合检索参数
top_k_embedding = 10  # Embedding阶段候选数量
top_k_final = 5      # 最终返回结果数量
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [QwenLM](https://github.com/QwenLM) - 提供优秀的Qwen3模型
- [ModelScope](https://modelscope.cn/) - 模型托管平台
- [Ray](https://ray.io/) - 分布式计算框架
- [Chroma](https://www.trychroma.com/) - 向量数据库
- [Streamlit](https://streamlit.io/) - Web应用框架

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 项目Issues: [GitHub Issues](https://github.com/SanroZhang/qwen3-ER-search/issues)

---

⭐ 如果这个项目对您有帮助，请给它一个星标！ 