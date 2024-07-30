FROM python:3.12-slim

RUN python3 -m pip install --no-cache-dir requests python-frontmatter pathlib

COPY . /
ENTRYPOINT ["python", "/entrypoint.py"]
