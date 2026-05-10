FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app
EXPOSE 8000
CMD ["sh", "-c", "uvicorn services.execution_orchestrator.app:app --host 0.0.0.0 --port 8000"]
