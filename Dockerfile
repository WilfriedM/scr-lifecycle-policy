FROM python:3.10-bullseye
LABEL maintainer="Wilfried Maillet <wilfried.maillet@emundus.fr>"

COPY scr-lifecycle-policy.py .
COPY requirements.txt .
COPY LICENSE .
COPY README.md .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt