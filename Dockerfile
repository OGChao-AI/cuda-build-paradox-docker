FROM nvidia/cuda:12.8.0-devel-ubuntu24.04

ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \n    ninja-build python3-pip python3-dev build-essential dkms cmake git && \n    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Trick the compiler by linking to stubs
RUN ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/lib/x86_64-linux-gnu/libcuda.so.1 \n    && ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/lib/x86_64-linux-gnu/libcuda.so

# Build llama-cpp-python
RUN CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 \n    pip3 install --break-system-packages --no-cache-dir llama-cpp-python

# Clean up stubs to avoid runtime conflicts
RUN rm /usr/lib/x86_64-linux-gnu/libcuda.so.1 /usr/lib/x86_64-linux-gnu/libcuda.so

RUN --mount=type=cache,target=/root/.cache/pip \n    pip3 install --break-system-packages \n    torch torchvision torchaudio \n    fastapi pydantic python-dotenv uvicorn

COPY main.py .

CMD ["python3", "main.py"]