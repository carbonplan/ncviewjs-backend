import re

import pydantic
import upath

from .models.pydantic import SanitizedURL


def parse_s3_url(url: str) -> tuple[str, str]:

    bucket = None
    key = None

    # https://bucket-name.s3.region-code.amazonaws.com/key-name

    if match := re.search('^https?://([^.]+).s3.([^.]+).amazonaws.com(.*?)$', url):
        bucket, key = match[1], match[3]

    # https://AccessPointName-AccountId.s3-accesspoint.region.amazonaws.com.
    if match := re.search(
        '^https?://([^.]+)-([^.]+).s3-accesspoint.([^.]+).amazonaws.com(.*?)$', url
    ):
        bucket, key = match[1], match[4]

    # S3://bucket-name/key-name
    if match := re.search('^s3://([^.]+)(.*?)$', url):
        bucket, key = match[1], match[2]

    return bucket, key


def parse_gs_url(url: str) -> tuple[str, str]:

    bucket = None
    key = None

    # https://storage.googleapis.com/carbonplan-share/maps-demo/2d/prec-regrid
    path = url.split('storage.googleapis.com/')[1]
    bucket, key = path.split('/', 1)
    return bucket, key


def parse_az_url(url: str) -> tuple[str, str]:

    bucket = None
    key = None

    if match := re.search('^https?://([^.]+).blob.core.windows.net(.*?)$', url):
        bucket, key = match[1], match[2]

    return bucket, key


def sanitize_url(url: pydantic.AnyUrl) -> SanitizedURL:
    """Sanitize a URL by removing any trailing slashes and parsing it with universal_pathlib"""

    # Remove trailing slashes
    url = url.rstrip("/")
    url_path = upath.UPath(url)
    parsed_url = url_path._url
    bucket = None
    key = None

    if parsed_url.scheme in {'http', 'https'}:
        if 'amazonaws.com' in parsed_url.netloc:
            bucket, key = parse_s3_url(url)

        elif 'googleapis.com' in parsed_url.netloc:
            bucket, key = parse_gs_url(url)

        elif 'blob.core.windows.net' in parsed_url.netloc:
            bucket, key = parse_az_url(url)

        else:
            bucket, key = parsed_url.netloc, parsed_url.path

    elif parsed_url.scheme in {'s3', 'gs', 'az', 'abfs'}:
        bucket, key = parsed_url.netloc, parsed_url.path

    return SanitizedURL(url=str(url), protocol=parsed_url.scheme, key=key, bucket=bucket)
