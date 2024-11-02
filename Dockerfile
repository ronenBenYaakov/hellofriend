# Use a specific version of the Python base image for consistency
FROM python:3.11-slim

# Set environment variables to prevent Python from writing pyc files and to disable buffering
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Update the package list and install necessary packages in a single RUN command
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    pip install --upgrade pip setuptools && \
    pip install --no-cache-dir flask_socketio flask_login flask_wtf flask_sqlalchemy wtforms flask_bcrypt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .z

# Specify the command to run your application
CMD ["python", "-m", "run", "--host=0.0.0.0"]
