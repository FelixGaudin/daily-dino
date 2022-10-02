FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV TZ="Europe/Amsterdam"

CMD ["python3", "get_dino.py"]