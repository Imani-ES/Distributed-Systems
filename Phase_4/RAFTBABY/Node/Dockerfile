FROM python:3.7-alpine3.14

RUN pip install flask
RUN pip install flask-socketio
# Stop the cache
ADD https://www.google.com /time.now 

COPY . .

EXPOSE 5555

ENTRYPOINT ["python", "-u", "node.py"]