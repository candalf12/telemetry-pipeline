FROM python:3.9-slim

WORKDIR /app

# download the library.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# begin.
CMD ["python", "-u", "main.py"] 