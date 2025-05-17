# API de Códigos Postales de México 🇲🇽

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

API REST para consulta de códigos postales mexicanos con base de datos normalizada, frontend integrado y despliegue Docker.

## Características Principales 🚀

- Base de datos PostgreSQL normalizada (3NF)
- API REST con FastAPI y documentación OpenAPI integrada
- Frontend responsive con TailwindCSS
- Configuración Docker lista para producción
- Búsqueda por código postal y filtrado por zona
- Estadísticas de distribución urbano/rural

## Tecnologías Utilizadas 💻

| Componente       | Tecnologías                                                                 |
|------------------|-----------------------------------------------------------------------------|
| Backend          | FastAPI, Python 3.11, SQLAlchemy, Uvicorn                                  |
| Base de Datos    | PostgreSQL 15, PgAdmin 4                                                   |
| Frontend         | HTML5, TailwindCSS (CDN), JavaScript vanilla                               |
| Infraestructura  | Docker, Docker Compose                                                     |
| Herramientas     | Git, GitHub, Pydantic, psycopg2-binary                                     |

## Instalación y Uso ⚙️

### Requisitos Previos
- Docker y Docker Compose
- Git (opcional)

### Con Docker (Recomendado)
```bash
# 1. Clonar repositorio
git clone git@github.com:Antonio-SZ1/codigos-postales-api.git
cd codigos-postales-api

# 2. Iniciar servicios
docker-compose up --build

# 3. Acceder a los componentes
API Docs: http://localhost:8000/docs
Frontend: http://localhost:8000/static/index.html
PostgreSQL: jdbc:postgresql://localhost:5432/codigos_postales
