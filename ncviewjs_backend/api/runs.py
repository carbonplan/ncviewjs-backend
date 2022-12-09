from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..database import get_session
from ..logging import get_logger
from ..models.dataset import RechunkRun

router = APIRouter()
logger = get_logger()


@router.get("/", response_model=list[RechunkRun], summary="Get a list of all rechunk runs")
def list_rechunk_runs(session: Session = Depends(get_session)):
    return session.exec(select(RechunkRun)).all()
