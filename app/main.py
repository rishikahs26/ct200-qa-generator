from fastapi import FastAPI
from app.database import Base, engine
from app.routers import documents, selections, generations

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CT-200 QA System")

app.include_router(documents.router)
app.include_router(selections.router)
app.include_router(generations.router)


@app.get("/")
def root():
    return {"status": "ok"}