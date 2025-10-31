# Use Python 3.13 as specified in pyproject.toml
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
# Download the 0.9.6 installer
ADD https://astral.sh/uv/0.9.6/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Copy project files in correct order for better caching
COPY . .

# Install dependencies only (no dev dependencies, no cache)
RUN uv sync --frozen --no-dev --no-cache

# Expose Streamlit port
EXPOSE 8501

# Run the Streamlit app without syncing (avoid installing dev dependencies)
ENTRYPOINT ["uv", "run", "--no-sync", "streamlit", "run", "agriphyto_schema/app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
