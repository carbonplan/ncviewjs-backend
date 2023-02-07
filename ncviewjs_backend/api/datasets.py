import contextlib
import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm.exc import NoResultFound
from sqlmodel import Session, select

from ..database import get_session
from ..dataset_processing import process_dataset
from ..helpers import sanitize_url
from ..logging import get_logger
from ..models.dataset import Dataset, DatasetRead, DatasetWithRechunkRuns, RechunkRun
from ..schemas.dataset import StorePayload

router = APIRouter()
logger = get_logger()


@router.post("/", response_model=DatasetRead, status_code=201, summary="Register a dataset")
def register_dataset(
    payload: StorePayload,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
) -> Dataset:
    """Store a dataset in the database."""
    logger.info(f"Storing dataset: {payload.url}")
    sanitized_url = sanitize_url(url=payload.url)

    # Check if dataset already exists
    dataset_exists = False

    with contextlib.suppress(NoResultFound):
        dataset = session.exec(select(Dataset).where(Dataset.md5_id == sanitized_url.md5_id)).one()

        logger.info(f"Dataset already stored: {dataset.url}")
        dataset_exists = True
    if dataset_exists and not payload.force:
        logger.info(f"Dataset already stored: {dataset.url} and force Flag is {payload.force}")
        return dataset

    # else, update the existing dataset
    if dataset_exists:
        # Rechunk run
        rechunk_run = RechunkRun(dataset_id=dataset.id, status="queued")
        session.add(rechunk_run)
        session.commit()
        session.refresh(dataset)
        session.refresh(rechunk_run)
        logger.debug(f"Revalidating dataset: {dataset}")
    else:
        # else, register the dataset
        dataset = Dataset(
            md5_id=sanitized_url.md5_id,
            url=sanitized_url.url,
            bucket=sanitized_url.bucket,
            key=sanitized_url.key,
            protocol=sanitized_url.protocol,
        )

        session.add(dataset)
        session.commit()

        # Rechunk run
        rechunk_run = RechunkRun(dataset_id=dataset.id, status="queued")

        session.add(rechunk_run)
        session.commit()
        session.refresh(dataset)
        session.refresh(rechunk_run)

        logger.debug(f"Created Rechunk run: {rechunk_run}")
        logger.debug(f"Create Dataset: {dataset}")

    background_tasks.add_task(
        process_dataset, dataset=dataset, rechunk_run=rechunk_run, session=session
    )
    return dataset


@router.get("/{id}", response_model=DatasetWithRechunkRuns, summary="Get a dataset by ID")
def get_dataset_by_id(
    id: int,
    latest: bool = Query(
        default=True,
        description='Whether to filter out rechunk runs and return the latest run only',
    ),
    session: Session = Depends(get_session),
) -> Dataset:
    """Get a dataset from the database."""
    logger.info(f"Getting dataset: {id}")
    dataset = session.get(Dataset, id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    dataset.last_accessed = datetime.datetime.now(datetime.timezone.utc)
    session.add(dataset)
    session.commit()
    session.refresh(dataset)

    if latest and len(dataset.rechunk_runs) > 1:
        logger.info("Filtering out rechunk runs and returning the latest run only")
        dataset.rechunk_runs = [max(dataset.rechunk_runs, key=lambda x: x.id)]

    return dataset


@router.get("/", response_model=list[DatasetWithRechunkRuns])
def list_datasets(session: Session = Depends(get_session)):
    return session.exec(select(Dataset)).all()
