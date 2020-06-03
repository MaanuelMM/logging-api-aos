FROM python:3.8.3-alpine

WORKDIR /usr/src/app

COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/. .

CMD ["python", "./app.py"]
