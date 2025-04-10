
# FROM python:3.12-slim
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

ADD . /app
WORKDIR /app
RUN uv sync --frozen
# RUN pip install --no-cache-dir uv
# # COPY requirements.txt .
# COPY pyproject.toml .
# RUN uv sync --all-extras
# # RUN pip install --no-cache-dir -r requirements.txt
#
# COPY . .

EXPOSE 8000 8501
ENV PATH = "./venv/bin:$PATH"
CMD ["bash", "start.sh"]
