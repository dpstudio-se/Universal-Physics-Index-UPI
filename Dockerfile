FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY data ./data
COPY schemas ./schemas

RUN pip install --no-cache-dir -e ".[postgres]"

EXPOSE 8080
CMD ["upi", "serve", "--host", "0.0.0.0", "--port", "8080"]
