from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv, set_key
import json
from typing import Optional, List
import os

app = FastAPI()
from .metric import Model
from .data import extract_info, get_tweets_by_date, divide_tweets_by_period_text


# Request classes
class CoordinateRequest(BaseModel):
    word: str
    provider: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ModelRequest(BaseModel):
    provider: str

class EnvUpdate(BaseModel):
    api_key: str
    provider: str


# Global variables start

llm = Model()
tweets:List
tweets = []

# Global variables end



# The following functions are the endpoints for the API

@app.post("/upload-tweets")
async def upload_file(file: UploadFile = File(...)):
    """
    Uploads a JSON file containing tweets and extracts the tweet content.
    ----------
    Args:
        file: UploadFile - is a file object that contains the JSON file.
    Returns:
        JSONResponse - returns a JSON response with a message. The message is either a success message or an error message.
    """

    global tweets
    tweet_content = {}
    if file.filename.endswith('.json'):
        file_content = await file.read()
        try:
            file_content_json = json.loads(file_content)
            tweet_content = file_content_json
            tweets = extract_info(tweet_content)
            return {"message": "JSON file uploaded successfully", "status": "success"}
        except json.JSONDecodeError:
            return JSONResponse(status_code=400, content={"message": "Invalid JSON File", "status": "error"})
    else:
        return JSONResponse(status_code=400, content={"message": "Please upload a JSON File!", "status": "error"})

@app.post("/load-model")
async def load_model(request: ModelRequest):
    """
    This function loads the model for the given provider in the request.
    It uses the load_model function from the Model class to load the model.
    ----------
    Args:
        request: ModelRequest - is a pydantic model that contains the provider name.
    Returns:
        JSONResponse - returns a JSON response with a message. The message is either a success message or an error message.
    """
    global llm
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
    """
    UNUSED. This function is not used in the current version of the application.
    This function returns the status of the model.
    ----------
    Returns:
        dict - returns a dictionary with the provider name and whether the model is loaded or not.
    """
    return {
        "provider": llm.provider if llm else None,
        "model_loaded": llm.model is not None if llm else False
    }

@app.post("/get-coords")
async def get_coordinates(request: CoordinateRequest):
    """
    This function returns the coordinates for the given word.
    It divides the tweets into periods and calculates the coordinates for each period.
    It uses the give_rating function from the Model class to calculate the coordinates for each period.
    It then calculates the mean of the coordinates to get the final coordinates.
    ----------
    Args:
        request: CoordinateRequest - is a pydantic model that contains the word and the provider name.
    Returns:
        JSONResponse - returns a JSON response with the coordinates and the attributes.
    Raises:
        HTTPException - raises an HTTPException if the model is not loaded or if there are no tweets.
    """
    global llm, tweets
    try:
        if not llm or not llm.model:
            print("Model not loaded", type(llm), type(llm.model), llm.provider)
            return JSONResponse(
                status_code=400,
                content={"error": "Model not loaded. Please load the model first.", "status": "error"}
            )
        
        if not tweets:
            return JSONResponse(
                status_code=400,
                content={"error": "No tweets found. Please upload tweets first.", "status": "error"}
            )

        if request.start_date and request.end_date:
            tweets = get_tweets_by_date(tweets, request.start_date, request.end_date)
        period = 100
        tweet_text = divide_tweets_by_period_text(tweets, period)
        attributes = llm.create_words(request.word)
        ratings = []
        for text in tweet_text:
            ratings.append(llm.give_rating(text, request.word, attributes['x_aspect'], attributes['x_positive'], attributes['x_negative'], attributes['y_aspect'], attributes['y_positive'], attributes['y_negative']))
        
        mean_x = sum(rating[0] for rating in ratings) / len(ratings)
        mean_y = sum(rating[1] for rating in ratings) / len(ratings)
        mean_rating = (mean_x, mean_y)

        return {"coordinates": mean_rating, "attributes": attributes}
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
async def reset_state():
    """
    This function resets the state of the application.
    It unloads the model and resets the tweets list.
    ----------
    Returns:
        dict - returns a dictionary with a message that the state has been reset.
    """
    global llm, tweets
    llm.unload_model()
    tweets = [] 
    return {"message": "State has been reset"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/update-env")
async def update_env(env_update: EnvUpdate):
    """
    This function updates the environment variables API_KEY and PROVIDER.
    It uses the set_key function from the dotenv module to update the environment variables.
    ----------
    Args:
        env_update: EnvUpdate - is a pydantic model that contains the API key and the provider name.
    Returns:
        dict - returns a dictionary with a message that the application is launching.
    """
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
    """
    This function checks if the API key is present in the environment variables.
    ----------
    Returns:
        dict - returns a dictionary with a boolean value that indicates if the API key is present
    """
    load_dotenv()
    api_key = os.getenv("API_KEY")
    return {"has_api_key": bool(api_key)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)