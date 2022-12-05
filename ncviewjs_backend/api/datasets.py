from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..database import get_session
from ..models.dataset import Dataset

router = APIRouter()


@router.get("/")
def list_datasets(session: Session = Depends(get_session)):
    return session.exec(select(Dataset)).all()
