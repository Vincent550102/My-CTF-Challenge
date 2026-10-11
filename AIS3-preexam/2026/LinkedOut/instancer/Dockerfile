FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /instancer

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 35000

CMD ["gunicorn", "--workers", "1", "--threads", "8", "--bind", "0.0.0.0:35000", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
