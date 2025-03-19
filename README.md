# AutoSub - Gerador Automático de Legendas

O AutoSub é uma aplicação web para geração automática de legendas para vídeos. É possível fazer upload de arquivos de vídeo ou fornecer URLs de vídeos online, e o sistema gera legendas em inglês e português.

## Funcionalidades

- Upload de arquivos de vídeo
- Processamento de vídeos a partir de URLs
- Geração automática de legendas em inglês
- Tradução automática para português
- Gerenciamento de vídeos e legendas
- Autenticação e gerenciamento de usuários
- Visualização e edição de legendas
- Correção de legendas com base em transcrições manuais
- Geração de textos para redes sociais com base nas legendas
- Painel administrativo para gerenciamento de usuários

## Requisitos

- Docker e Docker Compose
- ou Python 3.8+ (para execução local)

## Iniciando com Docker

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/autosub.git
   cd autosub
   ```

2. Execute o script de inicialização:
   ```
   ./start.sh
   ```

3. Acesse a aplicação em http://localhost:5000

4. Faça login com as credenciais padrão:
   - Usuário: admin
   - Senha: admin123

## Iniciando Localmente (sem Docker)

Se preferir executar localmente sem Docker:

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/autosub.git
   cd autosub
   ```

2. Execute o script de inicialização local:
   ```
   ./start-local.sh
   ```

3. Acesse a aplicação em http://localhost:5000

## Scripts Utilitários

- `start.sh`: Inicia o sistema usando Docker
- `start-local.sh`: Inicia o sistema localmente sem Docker
- `check-db.sh`: Verifica o estado do banco de dados

## Verificando o Banco de Dados

Para verificar o estado do banco de dados, use:

```
./check-db.sh
```

Este comando mostrará as tabelas existentes e os dados armazenados no banco de dados.

## Usando a Aplicação

1. Faça login com suas credenciais
2. Acesse a página de Upload
3. Faça upload de um vídeo ou forneça uma URL
4. Opcionalmente, forneça uma transcrição manual para melhorar a precisão das legendas
5. Aguarde o processamento (pode demorar, dependendo do tamanho do vídeo)
6. Acesse a página de detalhes do vídeo para visualizar, editar ou baixar as legendas

## Administração de Usuários

Usuários com privilégios de administrador podem:

1. Criar novos usuários
2. Editar informações de usuários existentes
3. Ativar ou desativar contas de usuários
4. Conceder privilégios de administrador a outros usuários

O acesso ao painel de administração está disponível no menu de conta para usuários administradores.

## Estrutura do Projeto

- `app.py`: Ponto de entrada da aplicação
- `src/`: Código-fonte da aplicação
  - `controllers/`: Controladores da aplicação
  - `models/`: Modelos de dados
  - `templates/`: Templates HTML
  - `static/`: Arquivos estáticos (CSS, JS, imagens)
  - `utils/`: Utilitários
  - `migrations/`: Scripts de migração do banco de dados
- `uploads/`: Diretório para armazenar os vídeos enviados
- `docker-compose.yml`: Configuração do Docker Compose
- `Dockerfile`: Configuração do Docker

## Tecnologias Utilizadas

- Python
- Flask
- PostgreSQL
- Docker
- autosub (biblioteca de reconhecimento de fala)
- FFmpeg
- YouTube-DL
- Bootstrap

## Licença

MIT
