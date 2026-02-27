from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth, users, tasks

app = FastAPI(title="Task Manager")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)


@app.get("/")
def root():
    return {"Created"}
