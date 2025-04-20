FROM python:3.11-slim

# Install system dependencies for Redis support
RUN apt-get update && apt-get install -y gcc

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file to leverage Docker's caching mechanism
COPY requirements.txt ./

# Install the dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
