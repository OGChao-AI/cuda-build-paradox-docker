from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama_cpp import Llama
from typing import Optional, List, Dict, Union, Any
from dotenv import load_dotenv
import os
import time
import asyncio
import gc
from contextlib import asynccontextmanager

load_dotenv()
MODELS_DIR = os.getenv("MODELS_DIR", "./models")
KEEP_ALIVE_SECONDS = int(os.getenv("KEEP_ALIVE_SECONDS", "10"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    bg_task = None
    if KEEP_ALIVE_SECONDS > 0:
        print(f"⏱️ Model keep-alive (TTL) enabled: {KEEP_ALIVE_SECONDS} seconds")
        bg_task = asyncio.create_task(unload_idle_model())
    yield
    if bg_task:
        bg_task.cancel()

app = FastAPI(title="CoreBot Llama-CPP Dynamic Server", lifespan=lifespan)

current_model_name: str = ""
llm: Optional[Llama] = None
last_access_time: float = 0.0

class Message(BaseModel):
    role: str
    content: Union[str, List[Dict[str, Any]]]

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: Optional[int] = 8000
    temperature: Optional[float] = 0.7

def get_or_load_model(model_name: str) -> Llama:
    global current_model_name, llm, last_access_time
    last_access_time = time.time()
    
    if '..' in model_name or model_name.startswith('/') or ':' in model_name:
        raise HTTPException(status_code=400, detail="Invalid model name. Path traversal detected.")

    if llm is not None and current_model_name == model_name:
        return llm

    model_path = os.path.join(MODELS_DIR, model_name)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}.")

    print(f"
🔄 Model switch requested. Loading: {model_name}...")
    if llm is not None:
        print(f"🧹 Unloading previous model: {current_model_name}...")
        del llm 
        gc.collect()

    llm = Llama(
        model_path=model_path,
        n_gpu_layers=-1,
        n_parallel=2,
        n_ctx=32768,
        flash_attn=True,
        verbose=False
    )
    current_model_name = model_name
    print("✅ Model loaded successfully!")
    return llm

async def unload_idle_model():
    global llm, current_model_name
    while True:
        await asyncio.sleep(10)
        if KEEP_ALIVE_SECONDS > 0 and llm is not None:
            idle_time = time.time() - last_access_time
            if idle_time > KEEP_ALIVE_SECONDS:
                print(f"
💤 Model '{current_model_name}' idle for {int(idle_time)}s. Unloading...")
                del llm
                llm = None
                current_model_name = ""
                gc.collect()

@app.post("/generate")
async def generate(request: ChatRequest):
    try:
        model_instance = get_or_load_model(request.model)
        msgs = [{"role": m.role, "content": m.content} for m in request.messages]
        output = model_instance.create_chat_completion(
            messages=msgs,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        text = output['choices'][0]['message']['content'].strip()
        return {"status": "success", "generated_text": text}
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "alive", "current_model": current_model_name}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)