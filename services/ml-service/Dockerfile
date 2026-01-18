FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "predict:app", "--host", "[IP_ADDRESS]", "--port", "8001"]