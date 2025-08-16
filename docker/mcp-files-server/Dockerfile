FROM python:3.12-slim
WORKDIR /app
COPY docker/mcp-files-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/mcp-connectors/files-server/app/ ./app/
EXPOSE 8087
CMD ["python", "app/server.py"]
