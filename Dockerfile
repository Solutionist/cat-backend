# COMP90024 Project - Team 34
# Lokesh Sai Sri Harsha Sankarasetty, Melbourne, [1130612]
# Kanch Vatcharotayan, Melbourne, [1132855]
# Sai Deepthi Amancha, Melbourne, [1051388]
# Josin Saji Abraham, Melbourne, [1129428]
# Kush Garg, Melbourne, [1146696]

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
COPY /requirements.txt /app/
RUN pip install -r requirements.txt
RUN apt update && apt -y upgrade
COPY . /app/
WORKDIR /app/
CMD exec uvicorn main:app --host ${SERVER_HOST} --port ${SERVER_PORT}