FROM python:3.11-slim

RUN useradd -m -u 1000 user

WORKDIR /app

COPY --chown=1000:1000 ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=1000:1000 . .

ENV APP_PORT=7255
EXPOSE 7255

USER 1000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7255"]
