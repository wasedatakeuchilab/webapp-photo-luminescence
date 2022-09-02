FROM python:3.10-bullseye as builder
RUN pip install -U pip \
 && pip install gunicorn
WORKDIR /work
COPY . /work
RUN pip install .

FROM python:3.10-slim-bullseye as runner
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
EXPOSE 8080
CMD [ "gunicorn", "-b", "0.0.0.0:8080", "webapp_photo_luminescence:server"]
