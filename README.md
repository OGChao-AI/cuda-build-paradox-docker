# CUDA Build Paradox Docker

This repository provides a battle-tested Docker configuration for building `llama-cpp-python` with CUDA support, specifically targeting high-end NVIDIA GPUs (like the RTX 5090).

## 🚀 The "Paradox" Fix
The core issue when building CUDA-enabled Python packages in Docker is the missing `libcuda.so` during the build phase (as it's provided by the driver at runtime, not the devel image). 

This project solves this by:
1. **Symlinking stubs**: Temporarily linking CUDA stubs to `/usr/lib/x86_64-linux-gnu/` to trick the compiler.
2. **Clean Build**: Compiling `llama-cpp-python` with `GGML_CUDA=on`.
3. **Cleanup**: Removing the symlinks immediately after the build to prevent runtime conflicts.

## 🛠️ Quick Start
1. Clone this repo.
2. Ensure you have the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) installed.
3. Run:
   ```
   docker compose up --build -d
   ```