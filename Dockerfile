FROM python:3.11-slim
WORKDIR /usr/src/app
COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock
COPY filechat.py ./
RUN useradd --create-home appuser
USER appuser
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "120", "filechat:app"]
