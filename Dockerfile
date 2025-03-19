FROM python:3.8-slim

# Instala dependências do sistema: FFmpeg e Git
RUN apt-get update && apt-get install -y ffmpeg git && rm -rf /var/lib/apt/lists/*

# Clona o repositório do autosub
RUN git clone https://github.com/agermanidis/autosub.git /opt/autosub

# Instala o autosub (modo editável) e as dependências da aplicação
RUN pip install --no-cache-dir -e /opt/autosub && \
    pip install Flask flask-basicauth gunicorn python-dotenv

# Define o diretório de trabalho e copia o código da aplicação e o arquivo .env
WORKDIR /app
COPY app.py /app/
COPY .env /app/

EXPOSE 5000

# Inicia a aplicação usando Gunicorn com timeout aumentado para 120 segundos
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120"]
