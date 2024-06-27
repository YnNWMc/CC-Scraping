FROM python:3.11

RUN apt-get update && apt-get install -y gcc pkg-config python-dev-is-python3 default-libmysqlclient-dev libssl-dev

WORKDIR /usr/app
RUN pip install --upgrade pip setuptools wheel

COPY . .

RUN pip install -r requirements.txt --verbose

CMD [ "python", "api-get.py" ]