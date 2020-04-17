FROM python:3.7
WORKDIR /usr/local/bin/app
COPY *.py ./
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["python3", "/usr/local/bin/app/Process.py"]