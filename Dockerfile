FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /root/.insightface/models/buffalo_l

COPY models/insightface/models/buffalo_l/* /root/.insightface/models/buffalo_l/

EXPOSE 8000
CMD ["sh", "scripts/run", "prod"]
