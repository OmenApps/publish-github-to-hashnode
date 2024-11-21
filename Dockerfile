FROM python:3.12-slim

COPY . /
RUN python3 -m pip install --no-cache-dir -r /requirements.txt
ENTRYPOINT ["python", "/entrypoint.py"]
