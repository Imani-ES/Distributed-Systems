FROM python:3.7-alpine3.14

RUN pip install flask
RUN pip install flask-socketio

COPY . .

EXPOSE 5555

ENTRYPOINT ["python", "-u", "node.py"]