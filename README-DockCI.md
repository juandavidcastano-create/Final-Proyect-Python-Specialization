# Proyecto Final — Docker y CI/CD

Instrucciones mínimas para Docker, Compose y GitHub Actions.

## Docker

Construir la imagen:

```bash
docker build -t proyecto-final:latest .
```

Ejecutar con Docker:

```bash
docker run -e DATABASE_URL="postgresql://postgres:postgres@host:5432/project_db" -p 8000:8000 proyecto-final:latest
```

## Docker Compose (desarrollo)

Levantar la app y la base de datos:

```bash
docker-compose up --build
```

La app quedará disponible en http://localhost:8000

## Tests en CI

Se incluye un workflow de GitHub Actions en `.github/workflows/ci.yml` que:
- Instala dependencias
- Levanta un servicio Postgres
- Ejecuta `alembic upgrade head`
- Ejecuta `pytest`
