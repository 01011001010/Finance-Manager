from fastapi import APIRouter
from . import account, transaction, delta, tag


router = APIRouter(prefix="/finance")

router.include_router(account.router)
router.include_router(transaction.router)
router.include_router(tag.router)
router.include_router(delta.router)
