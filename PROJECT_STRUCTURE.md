# Qwen3 Embedding & Reranker 检索系统 - 项目结构

## 📁 项目目录结构

```
qwen3_embedding/
├── 📂 src/                    # 源代码目录
│   ├── 📂 core/              # 核心功能模块
│   │   ├── test_qwen3_embedding.py    # Embedding模型测试
│   │   ├── test_qwen3_reranker.py     # Reranker模型测试
│   │   ├── hybrid_retrieval.py        # 混合检索系统
│   │   ├── hybrid_retrieval_db.py     # 带数据库的混合检索
│   │   ├── semantic_search.py         # 语义搜索示例
│   │   ├── search_name.py             # 姓名精确搜索
│   │   └── pdf_retrieval.py           # PDF检索工具
│   ├── 📂 api/               # API服务模块
│   │   ├── ray_qwen3.py              # Ray Serve API服务
│   │   └── embeeding4openai.py       # OpenAI兼容接口
│   ├── 📂 tools/             # 工具模块
│   │   └── vector_db_manager.py      # 向量数据库管理工具
│   └── 📂 utils/             # 工具函数模块（预留）
├── 📂 web/                   # Web界面模块
│   └── vector_db_viewer.py          # 向量数据库可视化工具
├── 📂 scripts/               # 脚本文件
│   ├── download_models.ps1          # 模型下载脚本（PowerShell）
│   ├── download_models.bat          # 模型下载脚本（Windows CMD）
│   ├── download_models.sh           # 模型下载脚本（Linux/Mac）
│   ├── start_viewer.bat             # 启动可视化工具（Windows）
│   └── start_viewer.ps1             # 启动可视化工具（PowerShell）
├── 📂 docs/                  # 文档目录
│   ├── README.md                    # 详细说明文档
│   ├── PROJECT_STRUCTURE.md         # 项目结构说明
│   ├── ray_config_guide.md          # Ray配置指南
│   ├── 向量数据库可视化软件使用说明.md  # 可视化工具使用说明
│   └── database_report.html         # 数据库报告
├── 📂 examples/              # 示例文件
│   └── client.ipynb                # Jupyter客户端示例
├── 📂 tests/                 # 测试文件
│   └── test_ray_api.py             # API测试
├── 📂 models/                # 模型文件目录（不包含在Git中）
├── 📂 vector_db/             # 向量数据库目录
├── requirements.txt          # 项目依赖
├── README.md                 # 项目主说明
└── .gitignore               # Git忽略文件
```

## 🎯 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 下载模型
```bash
# Windows PowerShell
.\scripts\download_models.ps1

# Windows CMD
scripts\download_models.bat

# Linux/Mac
chmod +x scripts/download_models.sh
./scripts/download_models.sh
```

### 3. 运行核心功能
```bash
# 测试Embedding模型
python src/core/test_qwen3_embedding.py

# 运行混合检索
python src/core/hybrid_retrieval_db.py
```

### 4. 启动Web界面
```bash
# 直接启动
python web/vector_db_viewer.py

# 或使用脚本启动
.\scripts\start_viewer.bat
```

### 5. 启动API服务
```bash
python src/api/ray_qwen3.py
```

## 📚 详细文档

- 📖 [完整README](docs/README.md) - 详细的项目说明
- 📖 [项目结构说明](docs/PROJECT_STRUCTURE.md) - 详细的项目结构说明
- 📖 [Ray配置指南](docs/ray_config_guide.md) - Ray Serve配置和使用指南
- 📖 [可视化工具使用说明](docs/向量数据库可视化软件使用说明.md) - Web界面使用指南

## 🔧 主要功能模块

### 核心功能 (`src/core/`)
- **Embedding模型**: 文本向量化，语义相似度计算
- **Reranker模型**: 文档相关性重排序
- **混合检索**: 结合Embedding和Reranker的两阶段检索
- **PDF支持**: PDF文档文本提取和检索
- **姓名搜索**: 精确姓名匹配功能

### API服务 (`src/api/`)
- **Ray Serve**: 提供RESTful API服务
- **OpenAI兼容**: 兼容OpenAI的Embedding接口

### 工具模块 (`src/tools/`)
- **数据库管理**: 向量数据库的批量导入、统计、导出

### Web界面 (`web/`)
- **可视化工具**: 基于Streamlit的数据库管理和可视化界面

## 🚀 特色功能

- ✅ **语义检索**: 基于Qwen3-Embedding的语义搜索
- ✅ **精准重排序**: 基于Qwen3-Reranker的精确排序
- ✅ **混合检索**: 两阶段检索策略，平衡速度和精度
- ✅ **向量数据库**: Chroma持久化存储
- ✅ **Web可视化**: 直观的数据库管理界面
- ✅ **API服务**: 生产级API接口
- ✅ **多平台支持**: Windows、Linux、MacOS
- ✅ **PDF支持**: 完整的PDF文档处理流程

---

⭐ 如果这个项目对您有帮助，请给它一个星标！ 