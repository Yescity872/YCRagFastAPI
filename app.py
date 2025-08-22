from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# from service.query_classifier import classify_query_with_gemini
from routers.tralli_router import router as tralli_router
import os

app = FastAPI()

# Enable CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryInput(BaseModel):
    query: str

@app.get('/')
def read_root():
    return {"message": "Yescity travel bot is running"}

# @app.post('/classify')
# def classify_user_query(input: QueryInput):
#     category = classify_query_with_gemini(input.query)
#     return {"category": category}

app.include_router(tralli_router)

# Server startup for production deployment
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)