#!/bin/bash
set -e

echo "🚀 Iniciando o AutoSub..."

# Usando as variáveis de ambiente definidas no docker-compose ou .env
# Não precisamos definir PGPASSWORD aqui, pois deve vir do ambiente

# Função para verificar se o banco de dados está acessível
function check_database() {
  echo "⏳ Aguardando conexão com o banco de dados..."
  
  # Tenta conectar ao banco de dados, com tempo limite de 60 segundos
  for i in {1..30}; do
    if pg_isready -h ${DB_HOST:-db} -U ${POSTGRES_USER:-postgres}; then
      echo "✅ Conexão com o banco de dados estabelecida!"
      return 0
    fi
    echo "⏳ Tentativa $i/30. Tentando novamente em 2 segundos..."
    sleep 2
  done
  
  echo "❌ Não foi possível conectar ao banco de dados. Tempo limite excedido."
  return 1
}

# Função para criar o banco de dados se não existir
function setup_database() {
  echo "🔧 Verificando se o banco de dados '${DB_NAME:-autosub}' existe..."
  
  # Usando variáveis de ambiente
  if ! PGPASSWORD="${POSTGRES_PASSWORD}" psql -h ${DB_HOST:-db} -U ${POSTGRES_USER:-postgres} -lqt | cut -d \| -f 1 | grep -qw ${DB_NAME:-autosub}; then
    echo "📦 Criando banco de dados '${DB_NAME:-autosub}'..."
    PGPASSWORD="${POSTGRES_PASSWORD}" psql -h ${DB_HOST:-db} -U ${POSTGRES_USER:-postgres} -c "CREATE DATABASE ${DB_NAME:-autosub};"
    echo "✅ Banco de dados '${DB_NAME:-autosub}' criado com sucesso!"
  else
    echo "✅ Banco de dados '${DB_NAME:-autosub}' já existe!"
  fi
}

# Verifica se o banco de dados está acessível
check_database

# Setup do banco de dados
setup_database

# Executando migrações
echo "🔄 Executando migrações do banco de dados..."
python -m src.migrations.migrations

# Iniciando a aplicação
echo "🌟 Iniciando o servidor Gunicorn..."
exec gunicorn app:app --bind 0.0.0.0:5000 --timeout 300 --workers 2 