#!/bin/bash

echo "🔍 Verificando o banco de dados do AutoSub..."
echo "------------------------------"

# Verificar se o container do banco está rodando
if ! docker ps | grep -q "autosub_db"; then
    echo "❌ Container do banco de dados não está rodando. Execute ./start.sh primeiro."
    exit 1
fi

# Executar comandos dentro do container do banco de dados
echo "📊 Tabelas existentes:"
docker exec -it autosub_db_1 psql -U postgres -d autosub -c "\dt"

echo ""
echo "👤 Usuários cadastrados:"
docker exec -it autosub_db_1 psql -U postgres -d autosub -c "SELECT id, username, email, full_name, is_active FROM users;"

echo ""
echo "🎬 Vídeos cadastrados:"
docker exec -it autosub_db_1 psql -U postgres -d autosub -c "SELECT id, user_id, title, status FROM videos;"

echo ""
echo "🔤 Legendas cadastradas:"
docker exec -it autosub_db_1 psql -U postgres -d autosub -c "SELECT id, video_id, language, format FROM subtitles;"

echo ""
echo "🔑 Sessões ativas:"
docker exec -it autosub_db_1 psql -U postgres -d autosub -c "SELECT id, user_id, expires_at FROM sessions;"

echo ""
echo "------------------------------"
echo "✅ Verificação do banco de dados concluída." 