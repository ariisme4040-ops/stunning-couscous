# Dockerfile

# Use the official Python 3.11 image from the Docker Hub
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Command to run the bot
CMD ["python", "bot.py"]
