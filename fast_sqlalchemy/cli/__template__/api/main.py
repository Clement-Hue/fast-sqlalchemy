from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from fast_sqlalchemy.cli.__template__.api.routes import router
from fast_sqlalchemy.cli.__template__.settings import config, db
from fast_sqlalchemy.persistence.middlewares import AutocommitMiddleware, DatabaseMiddleware


def create_app():
    app = FastAPI(title=config.get("project_name"),
                  description=config.get("description"),
                  version=config.get("version"))
    app.include_router(router)
    app.add_middleware(AutocommitMiddleware, db=db)
    app.add_middleware(DatabaseMiddleware, db=db)
    app.add_middleware(CORSMiddleware, allow_origins=config.get("cors_origin"),
                       allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

fastapi = create_app()