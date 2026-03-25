FROM python:3.12-slim

WORKDIR /app

# Install Poetry and package dependencies
RUN pip install --no-cache-dir poetry==2.0.1

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure poetry to install to system python
RUN poetry config virtualenvs.create false && \
    poetry install --with dev --no-interaction --no-ansi --no-root

# Copy source code
COPY src/ /app/src/
COPY data /app/data

ENV PYTHONPATH=/app/src
EXPOSE 8000

CMD ["uvicorn", "public_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
