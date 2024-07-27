from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv, set_key
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/run-script/")
def run_script():
    from .metric import your_function
    result = your_function()
    return {"result": result}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EnvUpdate(BaseModel):
    api_key: str
    provider: str

@app.post("/update-env")
async def update_env(env_update: EnvUpdate):
    try:
        # Load existing .env file
        env_path = ".env"  # Adjust this path as needed
        load_dotenv(env_path)

        set_key(env_path, "API_KEY", env_update.api_key)
        set_key(env_path, "PROVIDER", env_update.provider)

        return {"message": "Environment variables updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# TODO: Check if entered API key is valid or not.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)