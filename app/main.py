from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db.init_db import init_db
from app.routers.attendance import router as attendance_router
from app.routers.finance import router as finance_router
from app.routers.groups import router as groups_router
from app.routers.pages import router as pages_router
from app.routers.payments import router as payments_router
from app.routers.students import router as students_router
from app.routers.trainings import router as trainings_router

app = FastAPI(title="Sports School App")


@app.on_event("startup")
def on_startup():
    init_db()


app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(pages_router)
app.include_router(groups_router)
app.include_router(students_router)
app.include_router(trainings_router)
app.include_router(attendance_router)
app.include_router(payments_router)
app.include_router(finance_router)