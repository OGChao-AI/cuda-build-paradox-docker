# CUDA Build Paradox Docker

This repository provides a battle-tested Docker configuration for building `llama-cpp-python` with CUDA support, specifically targeting high-end NVIDIA GPUs (like the RTX 5060 Ti).

## 🚀 The "Paradox" Fix
The core issue when building CUDA-enabled Python packages in Docker is the missing `libcuda.so` during the build phase (as it's provided by the driver at runtime, not the devel image). 

This project solves this by:
1. **Symlinking stubs**: Temporarily linking CUDA stubs to `/usr/lib/x86_64-linux-gnu/` to trick the compiler.
2. **Clean Build**: Compiling `llama-cpp-python` with `GGML_CUDA=on`.
3. **Cleanup**: Removing the symlinks immediately after the build to prevent runtime conflicts.

## 🛠️ Quick Start

### 1. Install NVIDIA Container Toolkit (Prerequisite)
Before running the container, you must install the toolkit on your host machine to allow Docker to access your GPU:

```bash
# 添加 GPG 密钥和软件源
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \n  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \n    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \n    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 更新并安装 toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# 自动修改 /etc/docker/daemon.json 配置文件
sudo nvidia-ctk runtime configure --runtime=docker

# 重启 Docker 服务使配置生效
sudo systemctl restart docker
```

### 2. Launch the App
1. Clone this repo.
2. Run:
   ```bash
   docker compose up --build -d
   ```
