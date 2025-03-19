#!/bin/bash

echo "🚀 Iniciando o sistema AutoSub..."
echo "------------------------------"

# Verificar se temos o Docker e Docker Compose instalados
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker antes de continuar."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Por favor, instale o Docker Compose antes de continuar."
    exit 1
fi

# Criando diretórios necessários
echo "📁 Verificando diretórios necessários..."
mkdir -p uploads
mkdir -p src/static/{css,js,img}

# Garantir permissões
chmod -R 777 uploads

# Verificar se há containers antigos rodando
echo "🔄 Verificando containers antigos..."
if docker ps -q --filter "name=autosub" | grep -q .; then
    echo "🛑 Parando containers antigos..."
    docker-compose down
fi

# Limpar arquivos de cache
echo "🧹 Limpando arquivos de cache..."
find . -name "__pycache__" -type d -exec rm -rf {} +

# Construir e iniciar os containers
echo "🏗️ Construindo e iniciando os containers..."
docker-compose up -d

# Aguardar a inicialização completa
echo "⏳ Aguardando inicialização completa..."
sleep 15

# Verificar se os containers estão rodando
if ! docker ps | grep -q "autosub_app"; then
    echo "❌ Container da aplicação não está rodando. Verificando logs..."
    docker-compose logs app
    exit 1
fi

if ! docker ps | grep -q "autosub_db"; then
    echo "❌ Container do banco de dados não está rodando. Verificando logs..."
    docker-compose logs db
    exit 1
fi

# Verificar o endpoint de saúde
echo "🔍 Verificando o endpoint de saúde..."
HEALTH_STATUS=$(curl -s http://localhost:5000/health)
if echo $HEALTH_STATUS | grep -q "\"status\":\"ok\""; then
    echo "✅ Endpoint de saúde respondendo corretamente"
else
    echo "⚠️ Endpoint de saúde com problemas: $HEALTH_STATUS"
fi

# Verificar logs da aplicação
echo "📋 Logs da aplicação:"
docker logs autosub_app_1 | tail -n 20

echo ""
echo "✅ Sistema AutoSub iniciado com sucesso!"
echo "📊 Dashboard disponível em: http://localhost:5000"
echo "🔐 Credenciais padrão: admin / admin123"
echo "------------------------------"
echo "Para verificar os logs: docker-compose logs -f"
echo "Para parar o sistema: docker-compose down" 