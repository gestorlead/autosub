#!/bin/bash

echo "🚀 Iniciando o sistema AutoSub localmente..."
echo "------------------------------"

# Verificar se temos Python instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não está instalado. Por favor, instale o Python 3 antes de continuar."
    exit 1
fi

# Verificar se temos pip instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ Pip não está instalado. Por favor, instale o Pip antes de continuar."
    exit 1
fi

# Verificar se temos virtualenv
if ! command -v virtualenv &> /dev/null; then
    echo "📦 Instalando virtualenv..."
    pip3 install virtualenv
fi

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "🔧 Criando ambiente virtual..."
    virtualenv venv
fi

# Ativar ambiente virtual
echo "🔌 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -e git+https://github.com/agermanidis/autosub.git#egg=autosub
pip install Flask flask-basicauth gunicorn python-dotenv psycopg2-binary requests \
    PyYAML Werkzeug==2.3.7 youtube-dl bootstrap-flask Flask-SQLAlchemy Flask-Migrate \
    Flask-Login Flask-WTF email_validator Flask-Moment

# Criar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p uploads
mkdir -p src/static/{css,js,img,uploads}
chmod -R 777 uploads
chmod -R 777 src/static/uploads

# Configurar variáveis de ambiente
export FLASK_APP=app.py
export FLASK_ENV=development
export PYTHONPATH=.

# Iniciar o banco de dados PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️ PostgreSQL não está instalado localmente. Usando banco de dados SQLite."
    export DB_TYPE=sqlite
    export DB_PATH="./autosub.db"
else
    echo "🐘 Verificando PostgreSQL local..."
    if pg_isready &> /dev/null; then
        echo "✅ PostgreSQL está rodando localmente."
    else
        echo "⚠️ PostgreSQL não está rodando. Tentando iniciar..."
        if systemctl start postgresql &> /dev/null; then
            echo "✅ PostgreSQL iniciado com sucesso."
        else
            echo "⚠️ Não foi possível iniciar o PostgreSQL. Usando SQLite."
            export DB_TYPE=sqlite
            export DB_PATH="./autosub.db"
        fi
    fi
fi

# Executar migrações do banco de dados
echo "🔄 Configurando banco de dados..."
python -m src.migrations.setup_db

# Iniciar o aplicativo
echo "🌐 Iniciando o aplicativo Flask..."
echo "------------------------------"
echo "✅ Sistema iniciado! Acesse http://localhost:5000"
echo "🔐 Credenciais padrão: admin / admin123"
echo "------------------------------"
echo "Para parar o sistema: Ctrl+C"
echo ""

# Iniciar o servidor de desenvolvimento
python app.py 