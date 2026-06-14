# Imagem base leve com Python 3.12
FROM python:3.12-slim

# Evita arquivos .pyc e mantém logs sem buffer (aparecem em tempo real)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências de sistema necessárias para compilar o driver MySQL
# e a biblioteca bcrypt.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       default-libmysqlclient-dev \
       pkg-config \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Instala as dependências Python primeiro (aproveita cache do Docker
# enquanto o código da aplicação ainda não mudou)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Porta exposta pela aplicação dentro do container
EXPOSE 8000

# Healthcheck simples usado pelo Docker/orquestrador
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Em produção usamos Gunicorn com workers Uvicorn (assíncronos).
# O número de workers pode ser ajustado conforme os recursos da VPS.
CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "4", \
     "-b", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
