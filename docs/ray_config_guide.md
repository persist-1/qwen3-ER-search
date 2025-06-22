# Ray Serve 配置与使用指南

## 🚀 Ray 简介

Ray 是一个开源的分布式计算框架，专为机器学习和AI应用设计。在你的Qwen3检索系统中，Ray Serve用于部署和管理AI模型服务。

## 📊 核心概念

### 1. Ray Serve 架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HTTP Client   │───▶│   Ray Serve     │───▶│   Model Replica │
│                 │    │   Router        │    │   (GPU/CPU)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Model Replica │
                       │   (GPU/CPU)     │
                       └─────────────────┘
```

### 2. 部署配置参数

```python
@serve.deployment(
    num_replicas=NUM_REPLICAS,           # 副本数量
    ray_actor_options={
        "num_gpus": NUM_GPUS,           # GPU数量
        "num_cpus": 1,                  # CPU核心数
        "memory": 2000 * 1024 * 1024,   # 内存限制 (2GB)
    }
)
```

## 🎯 配置优化策略

### 1. GPU资源分配

#### 单GPU环境
```python
NUM_REPLICAS = 2
NUM_GPUS = 0.5  # 每个副本占用50% GPU
# 结果：两个副本共享一个GPU
```

#### 多GPU环境
```python
NUM_REPLICAS = 4
NUM_GPUS = 0.5  # 每个副本占用50% GPU
# 结果：4个副本分布在2个GPU上
```

#### 高负载环境
```python
NUM_REPLICAS = 6
NUM_GPUS = 0.3  # 每个副本占用30% GPU
# 结果：6个副本分布在2个GPU上，有负载均衡
```

### 2. 内存优化

```python
@serve.deployment(
    num_replicas=2,
    ray_actor_options={
        "num_gpus": 0.5,
        "memory": 4000 * 1024 * 1024,  # 4GB内存
        "object_store_memory": 1000 * 1024 * 1024,  # 1GB对象存储
    }
)
```

### 3. 网络配置

```python
serve.start(
    http_options=HTTPOptions(
        host="0.0.0.0",           # 监听所有网络接口
        port=4008,                # 服务端口
        root_path="/api/v1",      # API根路径
        max_concurrent_queries=100,  # 最大并发查询数
    )
)
```

## 🔧 性能调优

### 1. 批处理优化
```python
@app.post("/embedding/api")
def embedding(self, texts: EmbeddingInput):
    # 批处理多个文本
    batch_size = 32
    results = []
    
    for i in range(0, len(texts.input), batch_size):
        batch = texts.input[i:i+batch_size]
        with torch.inference_mode():
            output = self.emodel_embedding.encode(batch, is_query=texts.is_query)
            results.extend(output.cpu().detach().numpy().tolist())
    
    return results
```

### 2. 缓存机制
```python
from functools import lru_cache

class BatchCombineInferModel:
    def __init__(self, ...):
        self._cache = {}
    
    @lru_cache(maxsize=1000)
    def cached_encode(self, text: str, is_query: bool):
        return self.emodel_embedding.encode([text], is_query=is_query)
```

### 3. 异步处理
```python
import asyncio

@app.post("/embedding/api")
async def embedding_async(self, texts: EmbeddingInput):
    # 异步处理请求
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, 
        self.emodel_embedding.encode, 
        texts.input, 
        texts.is_query
    )
    return result.cpu().detach().numpy().tolist()
```

## 📈 监控和日志

### 1. 性能监控
```python
import time
from ray.serve import metrics

@app.post("/embedding/api")
def embedding(self, texts: EmbeddingInput):
    start_time = time.time()
    
    # 处理请求
    result = self.emodel_embedding.encode(texts.input, is_query=texts.is_query)
    
    # 记录指标
    processing_time = time.time() - start_time
    metrics.record_metric("embedding_latency", processing_time)
    metrics.record_metric("embedding_requests", 1)
    
    return result.cpu().detach().numpy().tolist()
```

### 2. 健康检查
```python
@app.get("/health")
def health_check(self):
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "gpu_usage": torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated(),
        "model_loaded": hasattr(self, 'emodel_embedding')
    }
```

## 🚀 部署最佳实践

### 1. 生产环境配置
```python
# 生产环境推荐配置
PRODUCTION_CONFIG = {
    "num_replicas": 4,           # 4个副本
    "num_gpus": 0.25,           # 每个副本25% GPU
    "num_cpus": 2,              # 2个CPU核心
    "memory": 8000 * 1024 * 1024,  # 8GB内存
    "max_concurrent_queries": 50,   # 最大并发50
}
```

### 2. 开发环境配置
```python
# 开发环境推荐配置
DEV_CONFIG = {
    "num_replicas": 1,           # 1个副本
    "num_gpus": 0.5,            # 50% GPU
    "num_cpus": 1,              # 1个CPU核心
    "memory": 4000 * 1024 * 1024,  # 4GB内存
    "max_concurrent_queries": 10,   # 最大并发10
}
```

### 3. 负载均衡
```python
# 自定义负载均衡策略
@serve.deployment(
    num_replicas=3,
    ray_actor_options={"num_gpus": 0.3}
)
class LoadBalancedModel:
    def __init__(self):
        self.request_count = 0
    
    @app.post("/api")
    def handle_request(self, request):
        self.request_count += 1
        # 根据负载选择处理策略
        if self.request_count > 100:
            # 高负载时的处理逻辑
            pass
        return self.process_request(request)
```

## 🔍 故障排除

### 1. 常见问题

#### GPU内存不足
```python
# 解决方案：减少GPU使用量
NUM_GPUS = 0.3  # 从0.9减少到0.3
```

#### 内存泄漏
```python
# 解决方案：定期清理缓存
import gc

@app.post("/api")
def api_with_cleanup(self, request):
    result = self.process(request)
    gc.collect()  # 强制垃圾回收
    return result
```

#### 网络超时
```python
# 解决方案：增加超时时间
serve.start(
    http_options=HTTPOptions(
        host="0.0.0.0",
        port=4008,
        request_timeout_s=300,  # 5分钟超时
    )
)
```

### 2. 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 添加调试端点
@app.get("/debug")
def debug_info(self):
    return {
        "gpu_memory": torch.cuda.memory_allocated(),
        "cpu_memory": psutil.virtual_memory().used,
        "active_requests": len(self._active_requests),
        "model_status": "loaded" if hasattr(self, 'model') else "not_loaded"
    }
```

## 📚 扩展阅读

- [Ray官方文档](https://docs.ray.io/)
- [Ray Serve教程](https://docs.ray.io/en/latest/serve/index.html)
- [Ray性能调优指南](https://docs.ray.io/en/latest/ray-core/performance/index.html)
- [Ray故障排除](https://docs.ray.io/en/latest/ray-core/troubleshooting/index.html) 