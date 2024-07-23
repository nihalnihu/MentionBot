FROM python:latest

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir --verbose

COPY . .

CMD ["python", "mention.py"]
