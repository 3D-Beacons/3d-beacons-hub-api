FROM python:3.12-slim
LABEL maintainer="Sreenath Sasidharan Nair sreenath@ebi.ac.uk"

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	UV_SYSTEM_PYTHON=1

WORKDIR /app

# Install uv for dependency resolution
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml README.md logging.conf ./
COPY app ./app
COPY worker ./worker

# Install application dependencies into the system environment
RUN uv pip install --system .

# EXPOSE 8000
CMD gunicorn --bind 0.0.0.0:8000 --conf /app/app/gunicorn_conf.py app.app:app
