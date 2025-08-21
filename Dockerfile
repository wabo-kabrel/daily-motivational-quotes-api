# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose port (Render will use $PORT)
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=motivation_api.app
ENV FLASK_ENV=production

# Start the app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "motivation_api.app:app"]
