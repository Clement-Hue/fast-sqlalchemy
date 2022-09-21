from fastapi import FastAPI


def create_app():
    app = FastAPI(title=config.get("project_name"),
                  description=config.get("description"),
                  version="1.0",
                  openapi_tags=config.get("openapi_tags"),
                  dependencies=[Depends(authentication(get_user_from_token))])

fastapi = create_app()