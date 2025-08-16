FROM python:3.12-slim
WORKDIR /app
COPY docker/mcp-box-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/mcp-connectors/box-server/app/ ./app/
EXPOSE 8086
CMD ["python", "app/server.py"]
