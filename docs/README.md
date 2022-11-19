# Docs

## Running ncviewjs-backend locally

To run the backend locally, you need to have both [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/) installed. Start by ensuring that you have Docker and Docker Compose:

```bash
docker --version

docker-compose --version
```

From the root of the repository, run the following command to the Docker image:

```bash
docker-compose build
```

This will take a while the first time you run it. Subsequent runs will be much faster.
Once the image is built, you can start the backend:

```bash
docker-compose up
```

This will start the backend on port 8004. You can now access the backend at http://localhost:8004.
