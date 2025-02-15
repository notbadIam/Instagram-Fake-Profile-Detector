FROM python:3.12

# Ensure system packages are updated
RUN apt update && apt install -y python3-distutils

# Upgrade pip and install required dependencies
RUN pip install --upgrade pip setuptools wheel

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# Command to run the application
CMD ["python", "app.py"]
