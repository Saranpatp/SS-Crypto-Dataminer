# Use an official Python runtime as the parent image
FROM python:3.9-slim

# Set the working directory in the Docker container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory (with your Python script) into the container
COPY . .

# Set an environment variable for thread limit
ENV THREAD_LIMIT=2

# Run your Python script when the container launches
CMD ["python", "./multi_exchange_socket_orderbook.py"]
