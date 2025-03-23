# AutoSub - Gerador Automático de Legendas

O AutoSub é uma aplicação web para geração automática de legendas para vídeos. É possível fazer upload de arquivos de vídeo ou fornecer URLs de vídeos online, e o sistema gera legendas em inglês e português.

![Versão](https://img.shields.io/badge/versão-1.1.5-blue)
![Licença](https://img.shields.io/badge/licença-MIT-green)

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
- Configurações personalizadas por usuário:
  - Escolha de serviço de transcrição (AutoSub ou Whisper)
  - Chaves API individuais (OpenAI, Google Translate)
  - Seleção de modelo OpenAI preferido
  - Prompts personalizados para redes sociais

## Requisitos

- Docker e Docker Compose
- ou Python 3.8+ (para execução local)

## Instalação com Docker

### Usando imagem pré-construída

```bash
# Baixar a imagem do Docker Hub
docker pull gestorlead/autosub:1.0.0

# Executar com Docker Compose
docker-compose up -d
```

### A partir do código-fonte

1. Clone o repositório:

   ```
   git clone https://github.com/gestorlead/autosub.git
   cd autosub
   ```

2. Execute o script de inicialização:

   ```
   ./start.sh
   ```

3. Acesse a aplicação em http://localhost:5000

## Iniciando Localmente (sem Docker)

Se preferir executar localmente sem Docker:

1. Clone o repositório:

   ```
   git clone https://github.com/gestorlead/autosub.git
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

### Configurações Personalizadas

Cada usuário pode personalizar sua experiência:

1. Acesse o menu de Configurações no canto superior direito
2. Configure suas preferências:
   - **Geral**: Escolha o serviço de transcrição padrão
   - **API**: Configure suas chaves API pessoais para OpenAI e Google Translate
   - **Modelos**: Selecione o modelo de IA preferido para geração de texto
   - **Prompts**: Personalize os prompts para geração de conteúdo para Instagram e TikTok

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
- `VERSION`: Arquivo com a versão atual do projeto
- `CHANGELOG.md`: Histórico de alterações do projeto

## Versionamento

Este projeto segue o [Versionamento Semântico 2.0.0](https://semver.org/lang/pt-BR/):

- MAJOR: alterações incompatíveis com versões anteriores
- MINOR: adição de funcionalidades mantendo compatibilidade
- PATCH: correções de bugs mantendo compatibilidade

Para ver o histórico de alterações, consulte o [CHANGELOG.md](CHANGELOG.md).

## Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Envie para o GitHub (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

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
