FROM python:3.12 as builder
WORKDIR /work
COPY . /work
# hadolint ignore=DL3013
RUN pip install --no-cache-dir .[uvicorn]

FROM python:3.12-slim as runner
LABEL org.opencontainers.image.title="DAWA for TRPL"
LABEL org.opencontainers.image.description="A web application for TRPL measurements"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.authors="Shuhei Nitta(@huisint)"
RUN useradd takeuchilab
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
EXPOSE 80
ENTRYPOINT [ "uvicorn", "dawa_trpl:server", "--host", "0.0.0.0" ]
CMD [ "--port", "80"]
