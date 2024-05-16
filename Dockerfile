FROM node:22-alpine as builder


COPY ./frontend/ /frontend
WORKDIR /frontend

RUN npm i -g @angular/cli

RUN ng build

FROM python:slim
RUN apt-get update --fix-missing && apt-get install -y --fix-missing build-essential
COPY --from=builder /frontend/dist/frontend/browser/ /frontend

COPY ./services /services
COPY ./requirements.txt /tmp/requirements.txt
COPY ./chroma_data /chroma_data

ARG GOOGLE_API_KEY
ENV GOOGLE_API_KEY=$GOOGLE_API_KEY
ENV FRONTEND_DIR=/frontend
ENV DB_DIR=/chroma_data
RUN pip install -r /tmp/requirements.txt

CMD ["uvicorn", "services:app", "--host", "0.0.0.0", "--port", "80"]
EXPOSE 80

