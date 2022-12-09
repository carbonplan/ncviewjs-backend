import pydantic
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm.exc import NoResultFound
from sqlmodel import Session, select

from ..database import get_session
from ..dataset_validation import validate_zarr_store
from ..helpers import sanitize_url
from ..logging import get_logger
from ..models.dataset import Dataset, RechunkRun
from ..schemas.dataset import StorePayload

router = APIRouter()
logger = get_logger()


def _validate_store(*, dataset: Dataset, rechunk_run: RechunkRun, session: Session) -> None:
    """Validate that the store is accessible"""
    try:
        validate_zarr_store(dataset.url)
    except Exception as exc:

        # update the rechunk run in the database
        rechunk_run.status = "completed"
        rechunk_run.outcome = "failure"
        rechunk_run.error_message = str(exc)
        session.add(rechunk_run)
        session.commit()
        session.refresh(rechunk_run)
        logger.error(f'Validation of store: {dataset.url} failed: {exc}')


@router.post("/", response_model=Dataset)
def post_dataset(
    payload: StorePayload,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
) -> Dataset:
    """Store a dataset in the database."""
    logger.info(f"Storing dataset: {payload.url}")
    sanitized_url = sanitize_url(url=payload.url)
    # Check if the dataset already exists in the database
    try:
        dataset = session.exec(select(Dataset).where(Dataset.md5_id == sanitized_url.md5_id)).one()
        logger.info(f"Dataset already stored: {dataset.url}")

    except NoResultFound:

        # Create a new dataset
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
            _validate_store, dataset=dataset, rechunk_run=rechunk_run, session=session
        )

    return dataset


@router.get("/{id}", response_model=Dataset)
def get_dataset_by_id(id: int, session: Session = Depends(get_session)) -> Dataset:
    """Get a dataset from the database."""
    logger.info(f"Getting dataset: {id}")
    dataset = session.get(Dataset, id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return dataset


# Get the dataset from the database using the url
@router.get("/", response_model=Dataset)
def get_dataset_by_url(
    url: pydantic.AnyUrl = Query(...), session: Session = Depends(get_session)
) -> Dataset:
    """Get a dataset from the database using the url."""
    logger.info(f"Getting dataset: {url}")
    sanitized_url = sanitize_url(url=url)
    dataset = session.exec(select(Dataset).where(Dataset.md5_id == sanitized_url.md5_id)).one()
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return dataset
