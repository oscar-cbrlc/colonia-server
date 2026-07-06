from fastapi import FastAPI

app = FastAPI(title="Colonia Server")

@app.get("/")
def home():
    return {'message':'Test App'}