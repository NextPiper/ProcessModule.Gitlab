FROM python:3.7
WORKDIR /usr/local/bin
COPY Process.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["python3", "/usr/local/bin/Process.py"]