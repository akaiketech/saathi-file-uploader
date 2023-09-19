# Use the official Python image as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 8502 for the FastAPI application
EXPOSE 8502

# Start the FastAPI application
CMD ["streamlit", "run", "main.py", "--server.port", "8502"]
