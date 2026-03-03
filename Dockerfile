FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY src/ src/
COPY scripts/ scripts/
RUN mkdir -p data
RUN chmod +x scripts/start.sh
EXPOSE 8000
CMD ["bash", "scripts/start.sh"]
