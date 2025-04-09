FROM ubuntu:24.04 AS builder

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libssl-dev \
    pkg-config \
    zlib1g-dev \
    && curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && curl -LsSf https://astral.sh/uv/install.sh | sh -s

RUN bash -c 'source "$HOME/.cargo/env" \
    && source "$HOME/.local/bin/env" \
    && uv python install 3.12 \
    && uv venv --python 3.12 \
    && uv pip install extractous '

RUN find ./root/.cache/uv -name *.so -path *bindings/extractous*  ! -path *release* -print -exec cp {} /.venv/lib/python3.12/site-packages/extractous/ \;

FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng

# set virtual env for uv
ENV VIRTUAL_ENV=/.venv/

RUN pip install uv \
    && uv venv

# Install extractous from builder stage
COPY --from=builder /.venv/lib/python3.12/site-packages/extractous /.venv/lib/python3.12/site-packages/extractous

WORKDIR /app

COPY extractous_src/requirements.txt .

RUN uv pip install --no-cache-dir -r requirements.txt

COPY . /app


# Set python path for uv run
ENV PYTHONPATH=.

CMD ["uv", "run", "--active", "extractous_src/main.py"]
# CMD ["sleep", "infinity"]

