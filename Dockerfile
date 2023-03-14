FROM python:latest
COPY src ./src
COPY requirements.txt /
RUN pip install -r requirements.txt
WORKDIR /src
CMD ["python", "app.py"]
