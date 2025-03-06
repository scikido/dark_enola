from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from check_username import WebsiteChecker

app = FastAPI()

# Define a Pydantic model for the request body
class UsernameRequest(BaseModel):
    username: str

# Initialize the WebsiteChecker with the data file
checker = WebsiteChecker('./data.json')

@app.post("/check-username/")
async def check_username(request: UsernameRequest):
    try:
        results = checker.check_username(request.username)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 