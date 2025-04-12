
# FROM python:3.12-slim
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app
# RUN mkdir -p /app/asf_mountpoint/app_storage/logs
# RUN mkdir -p /app/asf_mountpoint/app_storage/images
# RUN mkdir -p /app/asf_mountpoint/app_storage/images_treated
# Copy dependency files first (for better layer caching)
COPY pyproject.toml* requirements.txt* ./

# Install dependencies using uv
RUN if [ -f "pyproject.toml" ]; then \
      uv pip install --system -e .; \
    elif [ -f "requirements.txt" ]; then \
      uv pip install --system -r requirements.txt; \
    else \
      echo "No dependency file found"; \
      exit 1; \
    fi

# Add the rest of the code
COPY . .

# Create directory for output files with proper permissions
# RUN mkdir -p /app/API/images && chmod 777 /app/API/images

EXPOSE 8000 8501

CMD ["bash", "start.sh"]

