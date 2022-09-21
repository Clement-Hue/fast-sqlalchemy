from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from {PROJECT_NAME}.settings import config

def create_app():
    app = FastAPI(title=config.get("project_name"),
                  description=config.get("description"),
                  version=config.get("version"))
    app.add_middleware(CORSMiddleware, allow_origins=config.get("cors_origin"),
                       allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

fastapi = create_app()