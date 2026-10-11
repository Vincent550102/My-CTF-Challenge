FROM python:3.11-slim AS app-base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/app.py src/renderer.py ./
COPY src/lib ./lib
COPY src/uploads ./uploads
COPY src/templates ./templates
COPY smoke_tests.py /smoke_tests.py
RUN useradd -m -u 1000 ctf && chown -R ctf:ctf /app

CMD ["python", "app.py"]


FROM python:3.11-slim AS readflag-builder

WORKDIR /src

COPY readflag.c .
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev \
    && gcc -O2 -Wall -Wextra -o /readflag readflag.c \
    && strip /readflag \
    && rm -rf /var/lib/apt/lists/*


FROM app-base AS web

COPY --from=readflag-builder /readflag /readflag
RUN chown root:root /readflag && chmod 4755 /readflag && ln -sf /run/flag /flag


FROM app-base AS renderer
