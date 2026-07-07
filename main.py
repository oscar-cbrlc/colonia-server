from fastapi import FastAPI
from database import engine, Base
from routers import health

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Colonia API Server")

# routes van aquí
# app.include_router(users.router)
# app.include_router(tabla.router
app.include_router(health.router)