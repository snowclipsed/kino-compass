from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv, set_key
import json
from typing import Optional
import os

app = FastAPI()

# Assume these imports are correct and the functions are implemented
from .metric import load_model, is_slang, create_words, give_rating
from .data import load_tweets, extract_info, get_tweets_by_date, divide_tweets_by_period_text


class CoordinateRequest(BaseModel):
    word: str
    provider: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


tweets = {}

@app.post("/upload-tweets")
async def upload_file(file: UploadFile = File(...)):
    global tweets
    if file.filename.endswith('.json'):
        file_content = await file.read()
        try:
            file_content_json = json.loads(file_content)
            tweets = file_content_json
            return {"message": "JSON file uploaded successfully"}
        except json.JSONDecodeError:
            return {"message" : "Invalid JSON File"}
    else:
        return{"message":"Please upload a JSON File!"}

@app.get("/files/{filename}")
async def get_file(filename: str):
    if filename not in tweets:
        return JSONResponse(status_code=404, content={"message": "File not found"})
    
    return tweets[filename]


@app.post("/get-coords")
async def get_coordinates(request: CoordinateRequest):
    try:
        # Load model using the provider from the request
        model = load_model(provider=request.provider)
        print("Model loaded successfully", type(model))
        # Load tweets from the uploaded file
        extracted = extract_info(tweets)
        print("Extracted info successfully")
        
        if request.start_date and request.end_date:
            extracted = get_tweets_by_date(extracted, request.start_date, request.end_date)
        period = 80
        tweet_text = divide_tweets_by_period_text(extracted, period)
        
        print(f"Extracted text in period of {period} successfully")

        print(f"Checking if word {request.word} is slang")
        is_slang_word = is_slang(model, request.word)
        print("Checked if word is slang : ", is_slang_word)
        attributes = create_words(model, request.word, is_slang=is_slang_word)
        print("Created words successfully")
        print("Attributes : ", attributes)
        
        ratings = []
        for text in tweet_text:
            ratings.append(give_rating(text, model, request.word, attributes['x_meaning'], attributes['positive_x'], attributes['negative_x'], attributes['y_meaning'], attributes['positive_y'], attributes['negative_y']))
        
        mean_x = sum(rating[0] for rating in ratings) / len(ratings)
        mean_y = sum(rating[1] for rating in ratings) / len(ratings)
        mean_rating = (mean_x, mean_y)
        print("Rating: ", mean_rating)
        del model

        #TODO: FIGURE OUT HOW TO UNLOAD THE GPU MEMORY RELIABLY!
        return {"coordinates": mean_rating, "attributes": attributes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# TODO : FIGURE OUT HOW TO CANCEL THE REQUEST!
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

        return {"message": "Launching X Compass!"}
        # TODO : REMOVE THIS WHEN YOU ADD LOADING PAGE
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# TODO: Check if entered API key is valid or not.


@app.get("/check-api-key")
async def check_api_key():
    load_dotenv()
    api_key = os.getenv("API_KEY")
    return {"has_api_key": bool(api_key)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
