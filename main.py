import uvicorn
from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Agentic Swarm – Live Debate Engine")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
