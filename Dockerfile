FROM python:3.10-slim

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade  -r requirements.txt

COPY ./services ./services
ARG GOOGLE_API_KEY
ENV GOOGLE_API_KEY $GOOGLE_API_KEY

CMD ["uvicorn", "services:app", "--proxy-headers", "--host", "0.0.0.0", "--port" , "80"]

EXPOSE 80
