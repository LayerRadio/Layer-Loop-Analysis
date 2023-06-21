FROM python:3.11-slim-buster
WORKDIR /usr/src/app
ADD layeranalysis layeranalysis
# ADD webapp webapp
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
#Server will reload itself on file changes if in dev mode
ENV FLASK_ENV=development
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["flask", "run"]