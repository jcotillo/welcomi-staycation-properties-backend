# Use the official Python image from the Docker Hub
FROM python:3.12

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt
