FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup -m appuser

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Copy application code
COPY . .

# Create uploads directory and set ownership
RUN mkdir -p /app/uploads && chown -R appuser:appgroup /app \
    && mkdir -p /home/appuser/.cache && chown -R appuser:appgroup /home/appuser

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
