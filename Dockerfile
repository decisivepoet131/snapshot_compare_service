# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port configurable through an environment variable
ENV PORT=5000
ENV LOG_LEVEL=INFO
ENV LOG_RESULTS=FALSE

# Expose the port the app runs on
EXPOSE ${PORT}

# Define environment variable
ENV FLASK_APP=app.py

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=${PORT}"]