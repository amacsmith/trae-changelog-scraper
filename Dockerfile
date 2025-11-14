# Use Python 3.11 slim as base image
FROM python:3.11-slim

# Install cron, git, and other necessary packages
RUN apt-get update && \
    apt-get install -y cron git openssh-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the scraper script
COPY scraper.py .

# Make the script executable
RUN chmod +x scraper.py

# Create output directory
RUN mkdir -p /app/output/images

# Set up cron job to run every 15 minutes (96 times per day)
# Schedule: */15 * * * * (every 15 minutes)
RUN echo "*/15 * * * * cd /app && /usr/local/bin/python scraper.py >> /var/log/cron.log 2>&1" > /etc/cron.d/scraper-cron && \
    echo "" >> /etc/cron.d/scraper-cron && \
    chmod 0644 /etc/cron.d/scraper-cron && \
    crontab /etc/cron.d/scraper-cron && \
    touch /var/log/cron.log

# Run initial scrape on container start
RUN python scraper.py || true

# Create startup script that runs initial scrape and starts cron
RUN echo '#!/bin/bash\n\
echo "Starting Trae.ai Changelog Scraper..."\n\
echo "Running initial scrape..."\n\
python /app/scraper.py\n\
echo "Starting cron daemon..."\n\
cron\n\
echo "Cron started. Scraper will run every 15 minutes."\n\
tail -f /var/log/cron.log' > /app/start.sh && \
    chmod +x /app/start.sh

# Set environment variable for Python output
ENV PYTHONUNBUFFERED=1

# Expose a volume for output
VOLUME ["/app/output"]

# Start the service
CMD ["/app/start.sh"]
