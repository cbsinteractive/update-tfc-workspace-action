# syntax=docker/dockerfile:1
FROM frostedcarbon/tfc-cli:v1.1.0 AS get-tfc-cli
FROM python:3.9.9-slim-bullseye
COPY --from=get-tfc-cli ./tfc-cli /
COPY entrypoint.py /
ENTRYPOINT ["python", "/entrypoint.py"]
