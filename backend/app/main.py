from fastapi import FastAPI

from app.api.routes import router as api_router


# FastAPI 애플리케이션 진입점입니다.
app = FastAPI(title="Market Research API")
# API 라우트(예: /analyze)를 등록합니다.
app.include_router(api_router)
