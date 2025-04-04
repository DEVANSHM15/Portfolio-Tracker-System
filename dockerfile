# Use a base image with Python
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask port (if using Flask)
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
