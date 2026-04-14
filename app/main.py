from fastapi import FastAPI
from app.db.init_db import init_db
from app.routers.groups import router as groups_router
from app.routers.students import router as students_router

app = FastAPI(title="Sports School App")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"message": "App is running"}


app.include_router(groups_router)
app.include_router(students_router)