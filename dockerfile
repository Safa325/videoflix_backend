# Stage 1: Builder stage (install dependencies)
FROM python:3.11 AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create and set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.11

# Create non-root user and app directory
RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy application files (explicitly including entrypoint)
COPY --chown=appuser:appuser . /app/
COPY --chown=appuser:appuser entrypoint.prod.sh /app/entrypoint.prod.sh

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set permissions for entrypoint
RUN chmod +x /app/entrypoint.prod.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Run entrypoint
CMD ["/app/entrypoint.prod.sh"]