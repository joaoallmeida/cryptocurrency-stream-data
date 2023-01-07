FROM python:3.9-slim

EXPOSE 8501

WORKDIR /app

COPY ./scripts/dataVizualization.py /app
COPY ./requirements.txt  /app

RUN apt-get update && apt-get install -y
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

ENTRYPOINT ["streamlit","run","dataVizualization.py"]