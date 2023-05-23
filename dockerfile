FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY config/ config
COPY app/ app

CMD [ "python", "./main.py" ]