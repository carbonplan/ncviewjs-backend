# Docs



# Running ncviewjs-backend locally

&nbsp;  

 
## Creating a development environment

Using either mamba or conda, create a virtual environement using the supplied .yml configuration file. 

**Note: You can substitute `mamba` for `conda` if you do not have mamba installed**

In the top level of the project directory run:

```python

mamba env create --file environment-dev.yml python=3.10

```

Then activate the environment:

```bash

mamba activate ncviewjs

```

&nbsp;  

## Starting a postgres database

Follow this [link](https://postgresapp.com/) to download and start a postgres database instance.

### Setting Database URL as Environment Variable

In your terminal type:

``` export DATABASE_URL="postgres://postgres:@localhost:5432/postgres" ```

&nbsp;  


## Database migration


In the root directory of the project run:

```bash
alembic upgrade head
```

This should create the tables in the postgres database based upon the models defined in `models/`

To check that the tables exists in the local postgres database you can run in your terminal:

```console
 psql 
 ```

```console
psql (14.6)
Type "help" for help.
```

```console
postgres=# \c postgres
```

```console 
You are now connected to database "postgres" as user "postgres".
```

```console
postgres=# \dt
```

```console
              List of relations
 Schema |      Name       | Type  |  Owner
--------+-----------------+-------+----------
 public | alembic_version | table | postgres
 public | dataset         | table | postgres
 public | rechunkrun      | table | postgres
```

&nbsp;  


## Running tests

To run the tests, run the following command:

```bash
docker-compose exec web python -m pytest -v
```
