FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file to leverage Docker's caching mechanism
COPY requirements.txt ./

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the application directory for PyCharm
VOLUME /app

# Set the default command to run the application
CMD ["uvicorn", "main:app.py", "--reload"]

