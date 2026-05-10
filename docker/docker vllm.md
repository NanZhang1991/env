```bash
docker run --gpus all -itd  --name="Deepseek_r1_distill_qwen-14b_int4_awq"\
  -v /home/nanzhang/文档/models/LLM/Deepseek_r1_distill_qwen-14b_int4_awq:/mnt/models/Deepseek_r1_distill_qwen-14b_int4_awq \
  -p 9000:8000 \
  --ipc=host \
  vllm/vllm-openai:latest \
  -model /vllm-workspace/Deepseek_r1_distill_qwen-14b_int4_awq \
  --served-model-name deepseek_r1_14b_awq \
  --tensor-parallel-size 1 \
  --max-num-seqs 1 \
  --port 8000 \
  --gpu-memory-utilization 0.85 \
  --quantization awq \
  --enforce-eager \
  --max-model-len 1024
```

# 指定GPU
```bash
docker rm -f Deepseek_r1_distill_qwen-14b_int4_awq

docker run --gpus '"device=0"' -itd  --name="Deepseek_r1_distill_qwen-14b_int4_awq" \
  -e CUDA_VISIBLE_DEVICES=0 \
  -v /home/nanzhang/文档/models/LLM/Deepseek_r1_distill_qwen-14b_int4_awq:/vllm-workspace/Deepseek_r1_distill_qwen-14b_int4_awq \
  -p 9000:9000 \
  --ipc=host \
  vllm/vllm-openai:latest \
  --model /vllm-workspace/Deepseek_r1_distill_qwen-14b_int4_awq \
  --served-model-name deepseek_r1_14b_awq \
  --port 9000 \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.85 \
  --max-model-len 8192

docker network connect llm-net Deepseek_r1_distill_qwen-14b_int4_awq
docker logs -f Deepseek_r1_distill_qwen-14b_int4_awq
```


# 指定多GPU 使用容器内默认的8000端口
```bash
docker run --gpus '"device=0,1"' -itd  --name="Deepseek_r1_distill_qwen-14b_int4_awq" \
  -e CUDA_VISIBLE_DEVICES=0,1 \
  -v /home/nanzhang/文档/models/LLM/Deepseek_r1_distill_qwen-14b_int4_awq:/mnt/models/Deepseek_r1_distill_qwen-14b_int4_awq \
  -p 9000:8000 \
  --ipc=host \
  vllm/vllm-openai:latest \
  -model /vllm-workspace/Deepseek_r1_distill_qwen-14b_int4_awq \
  --served-model-name deepseek_r1_14b_awq \
  --tensor-parallel-size 2 \
  --gpu-memory-utilization 0.9 \
  --max-model-len 4096
```



curl http://Deepseek_r1_distill_qwen-14b_int4_awq:9000/v1/models


curl Deepseek_r1_distill_qwen-14b_int4_awq:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek_r1_14b_awq",
    "messages": [
      {"role": "user", "content": "你好，介绍一下你自己"}
    ]
  }'
  
curl http://localhost:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek_r1_14b_awq",
    "messages": [
      {"role": "user", "content": "你好，介绍一下你自己"}
    ]
  }'

# 下载的不完整
<!-- HF_ENDPOINT=https://hf-mirror.com \
hf download \
  --repo-type dataset \
  harborframework/terminal-bench-2.0 \
  --local-dir /home/nanzhang/文档/terminal-bench-2.0 -->


# habor 测试
## 数据集下载
```bash
sudo apt install git-lfs
git lfs install

git clone https://huggingface.co/datasets/harborframework/terminal-bench-2.0 \
  /data/datasets/terminal-bench-2.0

# 或走镜像
git clone https://hf-mirror.com/datasets/harborframework/terminal-bench-2.0 \
  /data/datasets/terminal-bench-2.0

git clone https://github.com/harbor-framework/terminal-bench-2 \
  /home/nanzhang/文档/terminal-bench-2.0
```

## 安装
```bash
uv tool install harbor
# 查找 harbor 实际位置
find ~/.local -name "harbor" 2>/dev/null
# 或者
uv tool dir
# 把 uv tool bin 目录加入 PATH
export PATH="$HOME/.local/bin:$PATH"
# 如果每次都要加，写入 ~/.bashrc：
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
# 验证
harbor --version
```

# 设置代理
```bash
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
```

```bash
# OPENAI_API_BASE=http://localhost:9000/v1 \
# LiteLLM / OpenAI SDK 强制要求 api_key
export OPENAI_API_KEY=not-needed

uv run harbor run \
--path /home/nanzhang/文档/datasets/terminal-bench-2.0 \
--agent terminus-2 \
--model openai/deepseek_r1_14b_awq \
--n-concurrent 1 \
--include-task-name sqlite-db-truncate \
--jobs-dir /home/nanzhang/文档/jobs \
--agent-kwarg api_base=http://localhost:9000/v1 \
--agent-kwarg temperature=0 \
--agent-kwarg max_turns=30 \
--agent-kwarg max_tokens=512
```

## 查看异常
```
find /home/nanzhang/文档/jobs/2026-05-11__02-03-27 -type f | head -20
cat /home/nanzhang/文档/jobs/2026-05-11__02-03-27/sqlite-db-truncate__YnL9ivB/exception.txt
```