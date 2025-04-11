# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 3003 available to the world outside this container
EXPOSE 3003

# Define environment variable
ENV NAME MCP_Server

# Run mcp_server.py when the container launches
CMD ["python", "mcp_server.py"] 