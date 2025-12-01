# Usar imagem Python slim
FROM python:3.12-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY pyproject.toml poetry.lock ./

# Instalar Poetry
RUN pip install poetry

# Configurar Poetry para não criar virtualenv
RUN poetry config virtualenvs.create false

# Instalar dependências
RUN poetry install --only=main --no-root

# Copiar código da aplicação
COPY src/ ./src/

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expor porta
EXPOSE 8000

# Comando para executar a aplicação
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
