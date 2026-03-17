# Dockerfile
# Use an official lightweight Python image as the base
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script into the container's working directory
COPY url_shortener.py .

# Specify the command to run when the container starts
CMD ["uvicorn", "url_shortener:app", "--host", "0.0.0.0", "--port", "8000"]
