# Use an official Python 3 runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose port 5000 for the Flask app
EXPOSE 5000

# Define environment variable to run Flask in production mode
ENV FLASK_ENV=production

# Run the Flask app when the container launches
CMD ["python3", "app.py"]

