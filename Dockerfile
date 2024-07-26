FROM python:3.12-slim

RUN python3 -m pip install --no-cache-dir requests python-frontmatter pathlib

COPY entrypoint.py /entrypoint.py
ENTRYPOINT ["python", "/entrypoint.py"]