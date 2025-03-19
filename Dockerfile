FROM python:3.8-slim

# Instala dependências do sistema: FFmpeg e Git
RUN apt-get update && apt-get install -y ffmpeg git postgresql-client curl && rm -rf /var/lib/apt/lists/*

# Clona o repositório do autosub
RUN git clone https://github.com/agermanidis/autosub.git /opt/autosub

# Instala o autosub (modo editável) e as dependências da aplicação
RUN pip install --no-cache-dir -e /opt/autosub && \
    pip install Flask flask-basicauth gunicorn python-dotenv psycopg2-binary requests \
    PyYAML Werkzeug==2.3.7 youtube-dl bootstrap-flask Flask-SQLAlchemy Flask-Migrate \
    Flask-Login Flask-WTF email_validator Flask-Moment

# Define o diretório de trabalho
WORKDIR /app

# Cria diretórios necessários
RUN mkdir -p /app/uploads && chmod 777 /app/uploads
RUN mkdir -p /app/src/static/uploads && chmod 777 /app/src/static/uploads

# Copia o código da aplicação
COPY . /app/

# Define as variáveis de ambiente
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py

# Aguarda 5 segundos para o banco de dados inicializar
EXPOSE 5000

# Script de inicialização que configura o banco de dados e inicia a aplicação
CMD ["sh", "-c", "sleep 10 && python -m src.migrations.setup_db && python -m src.migrations.add_is_admin_column && gunicorn app:app --bind 0.0.0.0:5000 --timeout 300 --workers 2"]
