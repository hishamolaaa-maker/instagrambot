import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routes import webhook, api, dashboard

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Create all DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Instagram DM Automation",
    description="ManyChat-style comment-to-DM automation using Instagram Graph API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(webhook.router, tags=["Webhook"])
app.include_router(api.router, tags=["API"])
app.include_router(dashboard.router, tags=["Dashboard"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
