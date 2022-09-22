from fastapi import APIRouter

from __template__.api import examples

router = APIRouter(prefix='/api')
router.include_router(examples.router, prefix="/examples", tags=["examples"])