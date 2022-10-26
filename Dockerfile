FROM python:3.10-bullseye as builder
RUN pip install -U pip
WORKDIR /work
COPY . /work
RUN pip install .[prod]

FROM python:3.10-slim-bullseye as runner
LABEL org.opencontainers.image.title="webapp photo luminescence"
LABEL org.opencontainers.image.description="A web application for photo luminescence measurements"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.authors="Shuhei Nitta(@huisint)"
RUN useradd takeuchilab
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
EXPOSE 80
CMD [ "uvicorn", "webapp_photo_luminescence:server", "--host", "0.0.0.0", "--port", "80"]
