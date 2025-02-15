FROM python:3.12-slim-bookworm

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"
ENV AIPROXY_TOKEN="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIyZjMwMDE4MzRAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9._wRoOghFlCA279Z9xgFn_sQLVSt9mBOunYxiPFNuNWI"

WORKDIR /app

COPY proj1 /app

CMD ["uv", "run", "app.py"]