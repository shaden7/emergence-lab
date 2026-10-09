FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .
COPY configs ./configs
RUN useradd --uid 10001 --create-home researcher
USER researcher
ENTRYPOINT ["emergence-lab"]
CMD ["--config", "configs/smoke.json", "--output", "/results"]
