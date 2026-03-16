from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.experiments import router as experiments_router
from app.api.proteins import router as proteins_router
from app.api.molecules import router as molecules_router
from app.api.simulation import router as simulation_router

app = FastAPI(
    title="Iteragen API",
    description="AI-driven drug discovery platform",
    version="0.4.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(experiments_router)
app.include_router(proteins_router)
app.include_router(molecules_router)
app.include_router(simulation_router)

@app.get("/")
def root():
    return {"status": "Iteragen API running", "version": "0.4.0"}

@app.get("/health")
def health():
    return {"status": "ok"}
