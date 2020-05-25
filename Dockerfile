FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
COPY /requirements.txt /app/
RUN apt update && apt -y upgrade
RUN pip install -r requirements.txt
COPY . /app/
WORKDIR /app/
CMD exec uvicorn main:app --host ${SERVER_HOST} --port ${SERVER_PORT}
