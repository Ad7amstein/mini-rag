# Alembic

## Run Alembic

### Configuration

```sh
cp alembic.ini.example alembic.ini
```

> Update the `alembic.ini` file with your database credentials (`sqlalchemy.url`).

### Initialize Alembic

```sh
alembic init alembic
```

### Create a new migration (Optional)

```sh
alembic revision --autogenerate -m "Add ..."
```

### Upgrade the database (head)

```sh
alembic upgrade head
```
