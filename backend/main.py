from fastapi import FastAPI
from routers import finance


app = FastAPI()
app.include_router(finance.router)


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "running"}
