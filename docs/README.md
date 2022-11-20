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

This will start the backend on port 8004. You can now access the backend at <http://localhost:8004>.

## Database migrations

The backend uses [Aerich](https://github.com/tortoise/aerich) for database migrations. To create a new migration, run the following command:

```bash
docker-compose exec web bash -i -c "aerich init -t app.db.TORTOISE_ORM"
```

This will create a config file called `ncviewjs-backend/pyproject.toml`:

```python
[tool.aerich]
tortoise_orm = "app.db.TORTOISE_ORM"
location = "./migrations"
src_folder = "./."
```

To create the first migration, run the following command:

```bash
docker-compose exec web bash -i -c "aerich init-db"
```

```console
Success create app migrate location migrations/models
Success generate schema for app "models"
```

That's it! You should now be able to see the two tables:

```bash
docker-compose exec web-db psql -U postgres
```

```console
psql (14.6)
Type "help" for help.

postgres=# \c web_dev
You are now connected to database "web_dev" as user "postgres".
web_dev=# \dt
         List of relations
 Schema |  Name  | Type  |  Owner
--------+--------+-------+----------
 public | aerich | table | postgres
 public | store  | table | postgres
(2 rows)
```

> **Note**
> The `aerich` documentation on database migration resides here: <https://tortoise-orm.readthedocs.io/en/latest/migration.html>
