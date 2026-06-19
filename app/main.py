from fastapi import FastAPI

from app.routes.user import router as user_router
from app.routes.project import router as project_router
from app.routes.document import router as document_router
from app.models import *
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Dashboard API")

app.include_router(user_router)
app.include_router(project_router)
app.include_router(document_router)


@app.get("/")
async def root():
    return {"message": "Project Dashboard API is running."}
