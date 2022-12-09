from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlmodel import Session, select

from ..database import get_session
from ..logging import get_logger
from ..models.dataset import RechunkRun, RechunkRunRead

router = APIRouter()
logger = get_logger()


@router.get("/", response_model=list[RechunkRunRead], summary="Get a list of all rechunk runs")
def list_rechunk_runs(session: Session = Depends(get_session)):
    return session.exec(select(RechunkRun)).all()


@router.get("/{id}", response_model=RechunkRunRead, summary="Get a rechunk run by id")
def get_rechunk_run(id: int, session: Session = Depends(get_session)):
    try:
        return session.exec(select(RechunkRun).where(RechunkRun.id == id)).one()
    except NoResultFound:
        raise HTTPException(status_code=404, content={"detail": f"Run with {id} not found"})

    except MultipleResultsFound:
        raise HTTPException(status_code=500, content={"detail": f"Multiple runs found for {id}"})
