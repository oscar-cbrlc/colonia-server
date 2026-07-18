from fastapi import FastAPI
from database import engine, Base
from routers import health, users, team, admin
from middleware import APIKeyMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Colonia API Server")

app.add_middleware(APIKeyMiddleware)

# routes de endpoints van aquí
# app.include_router(tabla.router
app.include_router(health.router)
app.include_router(users.router)
app.include_router(team.router)
app.include_router(admin.router)