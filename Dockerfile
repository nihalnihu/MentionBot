FROM docker pull python

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache gcc musl-dev

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["python", "mention.py"]
