FROM python:3.10-bullseye as builder
RUN pip install -U pip
WORKDIR /work
COPY . /work
RUN pip install .[prod]

FROM python:3.10-slim-bullseye as runner
LABEL org.opencontainers.image.title="DAWA for TRPL"
LABEL org.opencontainers.image.description="A web application for TRPL measurements"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.authors="Shuhei Nitta(@huisint)"
RUN useradd takeuchilab
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
EXPOSE 80
CMD [ "uvicorn", "dawa_trpl:server", "--host", "0.0.0.0", "--port", "80"]
