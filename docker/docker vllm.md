```bash
docker run --gpus all -itd  --name="Deepseek_r1_distill_qwen-14b_int4_awq"\
  -v /home/nanzhang/文档/models/LLM/Deepseek_r1_distill_qwen-14b_int4_awq:/mnt/models/Deepseek_r1_distill_qwen-14b_int4_awq \
  -p 9000:8000 \
  --ipc=host \
  vllm/vllm-openai:latest \
  -model /vllm-workspace/Deepseek_r1_distill_qwen-14b_int4_awq \
  --served-model-name deepseek_r1_14b_aqw \
  --tensor-parallel-size 1 \
  --max-num-seqs 1 \
  --port 8000 \
  --gpu-memory-utilization 0.9 \
  --quantization awq \
  --enforce-eager \
  --max-model-len 1024
```

# 指定GPU
```bash
docker run --gpus '"device=0"' -itd  --name="Deepseek_r1_distill_qwen-14b_int4_awq" \
  -e CUDA_VISIBLE_DEVICES=0 \
  -v /home/nanzhang/文档/models/LLM/Deepseek_r1_distill_qwen-14b_int4_awq:/vllm-workspace/Deepseek_r1_distill_qwen-14b_int4_awq \
  -p 9000:9000 \
  --ipc=host \
  vllm/vllm-openai:latest \
  --model /vllm-workspace/Deepseek_r1_distill_qwen-14b_int4_awq \
  --served-model-name deepseek_r1_14b_aqw \
  --port 9000 \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.9 \
  --max-model-len 1024
```


# 指定多GPU 使用容器内默认的8000端口
```bash
docker run --gpus '"device=0,1"' \
  -e CUDA_VISIBLE_DEVICES=0,1 \
  -v /home/nanzhang/文档/models/LLM/Deepseek_r1_distill_qwen-14b_int4_awq:/mnt/models/Deepseek_r1_distill_qwen-14b_int4_awq \
  -p 9000:8000 \
  --ipc=host \
  vllm/vllm-openai:latest \
  -model /vllm-workspace/Deepseek_r1_distill_qwen-14b_int4_awq \
  --tensor-parallel-size 2 \
  --gpu-memory-utilization 0.9 \
  --max-model-len 4096
```

