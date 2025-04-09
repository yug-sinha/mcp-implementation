# Use an official Python Alpine runtime as a parent image
FROM python:3.13-alpine

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that may be needed for building some Python packages.
# Adjust the list of packages based on your requirements.
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Default command to run the client; you can override this in docker-compose.
CMD ["python3", "client.py"]
