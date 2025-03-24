#!/bin/bash
set -e

echo "🚀 Iniciando o AutoSub..."

# Verificar se as variáveis de ambiente estão configuradas
if [ -z "$DB_HOST" ] || [ -z "$DB_PORT" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ] || [ -z "$DB_NAME" ]; then
  echo "❌ Erro: Variáveis de ambiente do banco de dados não configuradas corretamente."
  echo "Por favor, configure as variáveis DB_HOST, DB_PORT, DB_USER, DB_PASSWORD e DB_NAME."
  exit 1
fi

# Exibir as variáveis de ambiente usadas (sem mostrar a senha)
echo "Variáveis de ambiente do banco de dados:"
echo "DB_HOST=${DB_HOST}"
echo "DB_PORT=${DB_PORT}"
echo "DB_NAME=${DB_NAME}"
echo "DB_USER=${DB_USER}"

# Função para verificar se o banco de dados está acessível
function check_database() {
  echo "⏳ Aguardando conexão com o banco de dados..."
  
  for i in {1..30}; do
    if pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}"; then
      echo "✅ Conexão com o servidor PostgreSQL estabelecida!"
      
      # Verificar se o banco de dados existe
      if PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -lqt | cut -d \| -f 1 | grep -qw "${DB_NAME}"; then
        echo "✅ Banco de dados '${DB_NAME}' existe e está acessível."
        return 0
      else
        echo "❌ Erro: O banco de dados '${DB_NAME}' não existe."
        echo "Por favor, crie o banco de dados manualmente usando o comando:"
        echo "CREATE DATABASE ${DB_NAME};"
        return 1
      fi
    fi
    echo "⏳ Tentativa $i/30. Tentando novamente em 2 segundos..."
    sleep 2
  done
  
  echo "❌ Não foi possível conectar ao banco de dados. Tempo limite excedido."
  return 1
}

# Verifica se o banco de dados está acessível
if ! check_database; then
  echo "❌ Erro de conexão com o banco de dados. Verifique as configurações e garanta que o banco '${DB_NAME}' exista."
  exit 1
fi

# Executando migrações do banco de dados via Python
echo "🔄 Verificando e atualizando tabelas do banco de dados..."
python -m src.migrations.migrations

# Iniciando a aplicação
echo "🌟 Iniciando o servidor Gunicorn..."
exec gunicorn app:app --bind 0.0.0.0:5000 --timeout 300 --workers 2 