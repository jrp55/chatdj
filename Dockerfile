FROM python:3.10

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

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
