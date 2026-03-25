# eo-py-coding-challenge

This project consists of a FastAPI backend (`public_api`) and a React frontend (`user_interface`).

## Docker Setup

### Prerequisites
- Docker
- Docker Compose

### Running the Project

To build and run all services using Docker Compose:

```bash
docker compose up --build
```

- The API will be available at `http://localhost:8000`.
- The User Interface will be available at `http://localhost:5173`.

### Individual Service Build

To build only the `public_api` image:

```bash
docker build -t public-api ./public_api
```

To build only the `user_interface` image:

```bash
docker build -t user-interface ./user_interface
```

To run the containers manually:

```bash
docker run -p 8000:8000 public-api
docker run -p 5173:5173 user-interface
```
