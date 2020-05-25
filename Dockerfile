FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
COPY /requirements.txt /app/
RUN pip install -r requirements.txt --proxy="http://wwwproxy.unimelb.edu.au:8000/"
RUN echo 'Acquire::http::proxy "http://wwwproxy.unimelb.edu.au:8000/";Acquire::https::proxy "http://wwwproxy.unimelb.edu.au:8000/";' >> /etc/apt/apt.conf
RUN apt update && apt -y upgrade
COPY . /app/
WORKDIR /app/
CMD exec uvicorn main:app --host ${SERVER_HOST} --port ${SERVER_PORT}