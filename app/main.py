from fastapi import FastAPI

from app.routes.user import router as user_router
from app.routes.project import router as project_router

app = FastAPI(title="Project Dashboard API")

app.include_router(user_router)
app.include_router(project_router)


@app.get("/")
async def root():
    return {"message": "Project Dashboard API is running."}
