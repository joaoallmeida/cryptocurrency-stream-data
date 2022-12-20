FROM python:3.9-slim

EXPOSE 8501
EXPOSE 9093

WORKDIR /app

COPY ./scripts .
COPY requirements.txt .
COPY env.ini .

RUN apt-get update && apt-get install -y
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

# ENTRYPOINT ["streamlit", "run", "dataVizualization.py"]