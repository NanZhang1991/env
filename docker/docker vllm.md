```bash
docker run --gpus all -itd  --name="$model_name"\
  -v /home/nanzhang/文档/models/LLM/$model_name:/mnt/models/$model_name \
  -p 9000:8000 \
  --ipc=host \
  vllm/vllm-openai:latest \
  -model /vllm-workspace/$model_name \
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
docker rm -f $model_name

docker run --gpus '"device=0"' -itd  --name="$model_name" \
  -e CUDA_VISIBLE_DEVICES=0 \
  -e TZ=Asia/Shanghai \
  -v /home/nanzhang/文档/models/LLM/$model_name:/vllm-workspace/$model_name \
  -p 9000:9000 \
  --ipc=host \
  vllm/vllm-openai:latest \
  --model /vllm-workspace/$model_name \
  --served-model-name $model_name \
  --port 9000 \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.85 \
  --max-model-len 10240 \
  --max-num-seqs 1

docker network connect llm-net $model_name
docker logs -f $model_name
```


# 指定多GPU 使用容器内默认的8000端口
```bash
docker run --gpus '"device=0,1"' -itd  --name="$model_name" \
  -e CUDA_VISIBLE_DEVICES=0,1 \
  -v /home/nanzhang/文档/models/LLM/$model_name:/mnt/models/$model_name \
  -p 9000:8000 \
  --ipc=host \
  vllm/vllm-openai:latest \
  -model /vllm-workspace/$model_name \
  --served-model-name deepseek_r1_14b_awq \
  --tensor-parallel-size 2 \
  --gpu-memory-utilization 0.9 \
  --max-model-len 4096
```

# 测试
```bash
curl http://$model_name:9000/v1/models


curl $model_name:9000/v1/chat/completions \
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
```



# sglang
```bash
# export model_name=Qwen3-14B-AWQ
export model_name=gpt-oss-20b

docker rm -f $model_name

docker run --gpus '"device=0"' -itd  --name="$model_name" \
  -e CUDA_VISIBLE_DEVICES=0 \
  -e TZ=Asia/Shanghai \
  --shm-size 32g \
  -v /home/nanzhang/文档/models/LLM/$model_name:/workspace/$model_name \
  -p 30000:30000 \
  --ipc=host \
  lmsysorg/sglang:latest \
  python3 -m sglang.launch_server --model-path /workspace/$model_name --host 0.0.0.0 --port 30000 \
    --mem-fraction-static 0.85 \
    --max-total-tokens 112288 \
    --context-length 12048 \
    --chunked-prefill-size 2048 \
    --tensor-parallel-size 1 \
    --reasoning-parser gpt-oss \
    --strip-thinking-cache \
    --tool-call-parser gpt-oss

# [--reasoning-parser {deepseek-r1,deepseek-v3,glm45,hunyuan,gpt-oss,kimi,kimi_k2,mimo,qwen3,qwen3-thinking,minimax,minimax-append-think,step3,step3p5,mistral,nemotron_3,interns1,gemma4}]
#                     [--strip-thinking-cache]
#                     [--tool-call-parser {deepseekv3,deepseekv31,deepseekv32,glm,glm45,glm47,gpt-oss,kimi_k2,lfm2,llama3,mimo,mistral,pythonic,qwen,qwen25,qwen3_coder,step3,step3p5,minimax-m2,trinity,interns1,hermes,hunyuan,gigachat3,gemma4}]
#                     [--tool-server TOOL_SERVER] [--sampling-defaults {openai,model}]

docker network connect llm-net $model_name

docker logs -f $model_name
```

# 测试大模型服务接口
```bash
curl http://localhost:30000/v1/models
curl http://localhost:30000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "${model_name}",
    "messages": [
      {"role": "user", "content": "你好，介绍一下你自己"}
    ]
  }'
```

# habor 测试
## 数据集下载
### hf download 下载的不完整
<!-- HF_ENDPOINT=https://hf-mirror.com \
hf download \
  --repo-type dataset \
  harborframework/terminal-bench-2.0 \
  --local-dir /home/nanzhang/文档/terminal-bench-2.0 -->

### git-lfs
```bash
sudo apt install git-lfs
git lfs install

git clone https://huggingface.co/datasets/harborframework/terminal-bench-2.0 \
  /home/nanzhang/文档/datasets/terminal-bench-2.0

# 或走镜像
git clone https://hf-mirror.com/datasets/harborframework/terminal-bench-2.0 \
  /home/nanzhang/文档/datasets/terminal-bench-2.0

git clone https://github.com/harbor-framework/terminal-bench-2 \
  /home/nanzhang/文档/datasets/terminal-bench-2.0
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

## 设置代理
```bash
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
```

## 测试
```bash
# LiteLLM / OpenAI SDK 强制要求 api_key
export OPENAI_API_KEY=not-needed
# claude-code  terminus-2
export task_name=cobol-modernization
export terminal_bench_2_path=/home/nanzhang/文档/datasets/terminal-bench-2.0
# 构建任务镜像
cd ${terminal_bench_2_path}/$task_name/environment
# docker build -t alexgshaw/$task_name:20251031 .
docker pull alexgshaw/$task_name:20251031

export model_name=gpt-oss-20b
harbor run \
--path ${terminal_bench_2_path} \
--agent terminus-2 \
--model openai/$model_name \
--n-concurrent 1 \
--include-task-name $task_name \
--jobs-dir /home/nanzhang/文档/models/eval/terminal-bench-2.0/$task_name \
--agent-timeout-multiplier 1800 \
--agent-kwarg api_base=http://localhost:30000/v1 \
--agent-kwarg temperature=0 \
--agent-kwarg max_turns=30 \
--agent-kwarg max_tokens=8192
```

## 查看异常
```
find /home/nanzhang/文档/jobs/2026-05-11__02-03-27 -type f | head -20
cat /home/nanzhang/文档/jobs/2026-05-11__02-03-27/sqlite-db-truncate__YnL9ivB/exception.txt
```

