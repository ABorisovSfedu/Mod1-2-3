# Python 3.11 slim base
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PIP_CONFIG_FILE=/dev/null \
    PIP_REQUIRE_HASHES=0 \
    PIP_CONSTRAINT=

WORKDIR /app

RUN python -m pip install --upgrade "pip==25.2"

RUN pip install --no-cache-dir --timeout 60 --retries 10 \
      --index-url https://pypi.org/simple \
      fastapi==0.115.0 \
      "uvicorn[standard]==0.30.6" \
      pydantic==2.9.2 \
      pydantic-settings==2.10.1 \
      stanza==1.10.1 \
      rapidfuzz==3.9.6 \
      pytest==8.3.3 \
      httpx==0.27.2 \
      pyyaml==6.0.2 \
      jsonschema==4.21.1 \
      python-dotenv==1.0.1

# код
COPY . /app

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
