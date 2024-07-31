from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv, set_key
import json
from typing import Optional
import os

app = FastAPI()
from .metric import Model, is_slang, create_words, give_rating
from .data import load_tweets, extract_info, get_tweets_by_date, divide_tweets_by_period_text


# Request classes
class CoordinateRequest(BaseModel):
    word: str
    provider: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ModelRequest(BaseModel):
    provider: str

# Global variables

llm = None
tweets = {}

@app.post("/upload-tweets")
async def upload_file(file: UploadFile = File(...)):
    global tweets
    if file.filename.endswith('.json'):
        file_content = await file.read()
        try:
            file_content_json = json.loads(file_content)
            tweets = file_content_json
            return {"message": "JSON file uploaded successfully", "status": "success"}
        except json.JSONDecodeError:
            return JSONResponse(status_code=400, content={"message": "Invalid JSON File", "status": "error"})
    else:
        return JSONResponse(status_code=400, content={"message": "Please upload a JSON File!", "status": "error"})

@app.get("/files/{filename}")
async def get_file(filename: str):
    if filename not in tweets:
        return JSONResponse(status_code=404, content={"message": "File not found"})
    
    return tweets[filename]

@app.post("/load-model")
async def load_model(request: ModelRequest):
    global llm
    if llm is None:
        llm = Model()
    try:
        llm.provider = request.provider
        llm.load_model()
        return {"message": f"Model loaded successfully for provider: {request.provider}"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model-status")
async def get_model_status():
    return {
        "provider": llm.provider if llm else None,
        "model_loaded": llm.model is not None if llm else False
    }

@app.post("/get-coords")
async def get_coordinates(request: CoordinateRequest):
    global llm
    try:
        if not llm or not llm.model:
            return JSONResponse(
                status_code=400,
                content={"error": "Model not loaded. Please load the model first.", "status": "error"}
            )
        
        if not tweets:
            return JSONResponse(
                status_code=400,
                content={"error": "No tweets found. Please upload tweets first.", "status": "error"}
            )

        extracted = extract_info(tweets)
        
        if request.start_date and request.end_date:
            extracted = get_tweets_by_date(extracted, request.start_date, request.end_date)
        period = 80
        tweet_text = divide_tweets_by_period_text(extracted, period)

        is_slang_word = is_slang(llm.model, request.word)
        attributes = create_words(llm.model, request.word, is_slang=is_slang_word)
        
        ratings = []
        for text in tweet_text:
            ratings.append(give_rating(text, llm.model, request.word, attributes['x_meaning'], attributes['positive_x'], attributes['negative_x'], attributes['y_meaning'], attributes['positive_y'], attributes['negative_y']))
        
        mean_x = sum(rating[0] for rating in ratings) / len(ratings)
        mean_y = sum(rating[1] for rating in ratings) / len(ratings)
        mean_rating = (mean_x, mean_y)

        return {"coordinates": mean_rating, "attributes": attributes}
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
async def reset_state():
    global llm, tweets
    llm.unload_model()
    tweets = {}
    return {"message": "State has been reset"}

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
        env_path = ".env"
        load_dotenv(env_path)

        set_key(env_path, "API_KEY", env_update.api_key)
        set_key(env_path, "PROVIDER", env_update.provider)

        return {"message": "Launching X Compass!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/check-api-key")
async def check_api_key():
    load_dotenv()
    api_key = os.getenv("API_KEY")
    return {"has_api_key": bool(api_key)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

