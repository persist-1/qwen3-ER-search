# 项目结构说明

## 📁 目录结构

```
qwen3_embedding/
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
│   ├── start_viewer.ps1             # 启动可视化工具（PowerShell）
│   ├── quick_test.bat               # 快速测试脚本（Windows）
│   └── quick_test.ps1               # 快速测试脚本（PowerShell）
├── docs/                         # 文档目录
│   ├── README.md                    # 详细说明文档
│   ├── PROJECT_STRUCTURE.md         # 项目结构说明
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
├── .venv/                         # Python虚拟环境
├── requirements.txt               # 项目依赖
└── .gitignore                     # Git忽略文件
```

## 📋 文件说明

### 核心模块 (src/core/)
- **test_qwen3_embedding.py**: Qwen3-Embedding模型测试和封装
- **test_qwen3_reranker.py**: Qwen3-Reranker模型测试和封装
- **hybrid_retrieval.py**: 混合检索系统（内存版本）
- **hybrid_retrieval_db.py**: 混合检索系统（数据库版本）
- **semantic_search.py**: 语义搜索示例
- **search_name.py**: 姓名精确搜索工具
- **pdf_retrieval.py**: PDF文档检索工具

### API模块 (src/api/)
- **ray_qwen3.py**: Ray Serve API服务
- **embeeding4openai.py**: OpenAI兼容的embedding接口

### 工具模块 (src/tools/)
- **vector_db_manager.py**: 向量数据库管理工具

### Web界面 (web/)
- **vector_db_viewer.py**: Streamlit Web可视化工具

### 脚本文件 (scripts/)
- **download_models.ps1/.bat/.sh**: 模型下载脚本
- **start_viewer.ps1/.bat**: 启动Web可视化工具
- **quick_test.ps1/.bat**: 快速测试脚本

### 测试文件 (tests/)
- **test_ray_api.py**: Ray API服务测试
- **test_add_document.py**: 文档添加功能测试
- **test_add_document_simple.py**: 简化文档添加测试
- **test_db_operations.py**: 数据库操作测试
- **simple_test.py**: 基础功能测试

### 文档 (docs/)
- **README.md**: 项目主要说明文档
- **PROJECT_STRUCTURE.md**: 项目结构说明
- **ray_config_guide.md**: Ray配置指南
- **向量数据库可视化软件使用说明.md**: Web工具使用说明
- **database_report.html**: 数据库报告

## 🚀 快速开始

### 1. 环境准备
```bash
# 激活虚拟环境
.venv\Scripts\Activate.ps1  # PowerShell
# 或
.venv\Scripts\activate.bat  # CMD
```

### 2. 运行测试
```bash
# 快速测试
.\scripts\quick_test.ps1

# 或单独测试
python tests\test_add_document_simple.py
```

### 3. 启动Web界面
```bash
# 使用脚本启动
.\scripts\start_viewer.ps1

# 或直接启动
streamlit run web\vector_db_viewer.py
```

### 4. 运行核心功能
```bash
# 测试embedding模型
python src\core\test_qwen3_embedding.py

# 运行混合检索
python src\core\hybrid_retrieval_db.py
```

## 📝 开发规范

### 文件命名
- Python文件使用小写字母和下划线
- 测试文件以`test_`开头
- 脚本文件使用描述性名称

### 目录组织
- 按功能模块分类
- 测试文件统一放在`tests/`目录
- 脚本文件统一放在`scripts/`目录
- 文档文件统一放在`docs/`目录

### 代码规范
- 使用UTF-8编码
- 遵循PEP 8代码风格
- 添加适当的注释和文档字符串 