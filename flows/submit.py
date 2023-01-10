from ncview_rechunk import rechunk
from prefect.deployments import Deployment
from prefect.filesystems import S3
from prefect_aws import AwsCredentials

if __name__ == "__main__":
    s3_block = S3.load('prod')
    creds = AwsCredentials.load('prod')

    deployment = Deployment.build_from_flow(
        flow=rechunk,
        name='ncviewjs',
        work_queue_name='prefectops',
        tags=['ncviewjs', 'rechunk'],
        storage=s3_block,
        apply=True,
        infra_overrides={
            "env.PREFECT_LOGGING_LEVEL": "DEBUG",
            "env.AWS_ACCESS_KEY_ID": creds.aws_access_key_id,
            "env.AWS_SECRET_ACCESS_KEY": creds.aws_secret_access_key.get_secret_value(),
            "env.AWS_DEFAULT_REGION": "us-west-2",
        },
    )
    deployment.apply()
