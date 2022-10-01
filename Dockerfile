ARG PORT=5000

FROM python:3.10

ARG PORT=5000
ENV PORT=${PORT}

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apt-get update && apt-get install -y libre2-dev && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pybind11 cmake cython && \
    pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y cython cmake pybind11 && \
    apt-get purge -y libre2-dev && \
    rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE ${PORT}

CMD ["sh", "-c", "gunicorn -w 2 -b 0.0.0.0:$PORT 'app:app'"]
