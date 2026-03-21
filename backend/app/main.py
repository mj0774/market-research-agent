from fastapi import FastAPI

from app.api.routes import router as api_router


app = FastAPI(title="Market Research API")
app.include_router(api_router)
