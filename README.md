# Autosub Web

Uma aplicação web para geração automática de legendas em vídeos com tradução para português.

## 🚀 Funcionalidades

- Upload de vídeos (suporta formatos MP4, MOV, AVI, MKV)
- Geração automática de legendas em inglês
- Tradução automática das legendas para português
- Download do arquivo de legendas (.srt)
- Interface web simples e intuitiva
- Autenticação básica para segurança

## 📋 Pré-requisitos

- Docker
- Docker Swarm (para deploy em produção)
- Chave de API do Google Translate

## 🔧 Configuração

1. Clone o repositório:

```bash
git clone https://github.com/gestorlead/autosub.git
cd autosub
```

2. Configure as variáveis de ambiente no arquivo `.env`:

```env
FLASK_SECRET_KEY=sua_chave_secreta
BASIC_AUTH_USERNAME=seu_usuario
BASIC_AUTH_PASSWORD=sua_senha
GOOGLE_TRANSLATE_API_KEY=sua_chave_google_translate
```

3. Configure o arquivo `auto-sub.yaml` conforme necessário para seu ambiente.

## 🚀 Deploy

### Desenvolvimento Local

1. Construa a imagem Docker:

```bash
docker build -t autosub-web .
```

2. Execute o container:

```bash
docker run -p 5000:5000 --env-file .env autosub-web
```

### Produção (Docker Swarm)

1. Inicialize o Docker Swarm (se ainda não estiver inicializado):

```bash
docker swarm init
```

2. Deploy do stack:

```bash
docker stack deploy -c auto-sub.yaml autosub
```

## 🌐 Uso

1. Acesse a aplicação através do navegador
2. Faça login com as credenciais configuradas
3. Selecione um arquivo de vídeo para upload
4. Aguarde o processamento
5. Faça o download do arquivo de legendas gerado

## 🛠️ Tecnologias Utilizadas

- Python
- Flask
- Autosub
- Google Cloud Translation API
- Docker
- Traefik (para proxy reverso e SSL)

## ⚠️ Notas Importantes

- Certifique-se de manter suas chaves de API e credenciais seguras
- O armazenamento de arquivos é temporário em `/tmp/uploads`
- Recomenda-se implementar um sistema de limpeza periódica para os arquivos temporários
- Em produção, configure corretamente o SSL através do Traefik

## 📄 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ✨ Contribuição

1. Faça um Fork do projeto
2. Crie sua Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request
