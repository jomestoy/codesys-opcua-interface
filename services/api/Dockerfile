FROM python:3.12-slim

WORKDIR /workspace
COPY pyproject.toml README.md ./
COPY codesys_opcua_interface ./codesys_opcua_interface
COPY services ./services
RUN python -m pip install --no-cache-dir -e .

ENV REAL_IO_ENABLED=false
ENV DEMO_MODE=true
EXPOSE 8000

CMD ["python", "-m", "services.api.run"]
