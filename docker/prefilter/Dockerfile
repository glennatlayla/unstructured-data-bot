FROM python:3.12-slim

WORKDIR /app

COPY services/prefilter/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/prefilter/ .

EXPOSE 8084

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8084"]
