FROM python:3.12-slim
WORKDIR /app
COPY docker/orchestrator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/orchestrator/app/ ./app/
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
