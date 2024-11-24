FROM python:3-alpine

ARG SECRET_KEY=fake-secret-key
ARG ALLOWED_HOSTS=localhost,127.0.0.1,::1,testserver

WORKDIR /app/polls

ENV SECRET_KEY=${SECRET_KEY}
ENV DEBUG=True
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS}
ENV TIME_ZONE=Asia/Bangkok

COPY ./requirements.txt .

# Install dependencies in Docker container
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x ./entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]