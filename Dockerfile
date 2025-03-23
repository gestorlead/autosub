FROM python:3.8-slim

# Instala dependências do sistema: FFmpeg e Git
RUN apt-get update && apt-get install -y ffmpeg git postgresql-client curl && rm -rf /var/lib/apt/lists/*

# Clona o repositório do autosub
RUN git clone https://github.com/agermanidis/autosub.git /opt/autosub

# Instala o autosub (modo editável) e as dependências da aplicação
RUN pip install --no-cache-dir -e /opt/autosub && \
    pip install Flask flask-basicauth gunicorn python-dotenv psycopg2-binary requests \
    PyYAML Werkzeug==2.3.7 youtube-dl bootstrap-flask Flask-SQLAlchemy Flask-Migrate \
    Flask-Login Flask-WTF email_validator Flask-Moment openai

# Define o diretório de trabalho
WORKDIR /app

# Cria diretórios necessários
RUN mkdir -p /app/uploads && chmod 777 /app/uploads
RUN mkdir -p /app/src/static/uploads && chmod 777 /app/src/static/uploads
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Copia o código da aplicação
COPY . /app/

# Tornar o entrypoint executável
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Define as variáveis de ambiente
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py

# Porta da aplicação
EXPOSE 5000

# Define o script de entrypoint que cuida da inicialização do banco e da aplicação
ENTRYPOINT ["/entrypoint.sh"]
