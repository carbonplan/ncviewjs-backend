from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlmodel import Session, select

from ..database import get_session
from ..logging import get_logger
from ..models.dataset import RechunkRun, RechunkRunPayload, RechunkRunRead

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


@router.patch("/{id}", response_model=RechunkRunRead, summary="Update a rechunk run by id")
def update_rechunk_run(
    id: int, payload: RechunkRunPayload, session: Session = Depends(get_session)
):
    try:
        logger.info(f"Updating rechunk run: {id} with {payload}")
        run = session.exec(select(RechunkRun).where(RechunkRun.id == id)).one()
        run.start_time = payload.start_time
        run.end_time = payload.end_time
        run.rechunked_dataset = payload.rechunked_dataset
        run.error_message = payload.error_message
        run.error_message_traceback = payload.error_message_traceback
        run.status = payload.status
        run.outcome = payload.outcome
        session.add(run)
        session.commit()
        session.refresh(run)
        return run
    except NoResultFound:
        raise HTTPException(status_code=404, content={"detail": f"Run with {id} not found"})

    except MultipleResultsFound:
        raise HTTPException(status_code=500, content={"detail": f"Multiple runs found for {id}"})
