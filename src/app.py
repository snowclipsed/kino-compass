from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/run-script/")
def run_script():
    # Import your script and run the desired function here
    from .metric import your_function
    result = your_function()
    return {"result": result}
