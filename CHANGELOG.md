# Changelog

## [1.1.6] - 2025-03-24

### Corrigido

- Problema de reinicialização do banco de dados ao reiniciar a aplicação
- Persistência de dados no PostgreSQL usando volume Docker corretamente configurado
- Remoção de logs de depuração excessivos para manter os logs mais limpos
- Verificação aprimorada da existência de tabelas para evitar recriação desnecessária

## [1.1.5] - 2025-06-10

### Adicionado

- Configurações personalizadas por usuário para melhor experiência de uso
- Painel de configurações de usuário com múltiplas opções de personalização
- Escolha de serviço de transcrição (AutoSub ou Whisper) por usuário
- Campos para armazenar chaves API individuais por usuário (OpenAI, Google Translate)
- Seleção de modelo OpenAI preferido para geração de texto
- Prompts personalizados para geração de conteúdo para Instagram e TikTok
- Migração simplificada do banco de dados para instalação mais rápida

### Melhorado

- Interface para configurações de usuário com feedback visual sobre opções selecionadas
- Sistema de armazenamento seguro de chaves API no banco de dados
- Lógica de processamento de vídeos adaptada para usar configurações do usuário
- Utilização de chaves API específicas do usuário para serviços externos
- Estrutura modular para facilitar a adição de novos serviços no futuro
- Sistema de fallback quando configurações específicas não estão disponíveis

### Corrigido

- Problema de dependência de variáveis de ambiente para chaves API
- Gerenciamento de configurações em ambientes multi-usuário
- Segurança nas rotas de configuração para proteger dados de usuários

## [1.1.4] - 2025-05-28

### Melhorado

- Aprimoramento do sistema de geração de legendas usando API Whisper
- Implementação de sistema robusto de logs para melhor rastreamento de erros
- Adição de campos para seleção de idiomas de origem e destino na interface de upload
- Adição de campo para especificar o número de pessoas falando no vídeo
- Suporte para diferentes combinações de idiomas na transcrição e tradução

## [1.1.3] - 2025-05-25

### Melhorias

- Melhoria de contraste no rodapé para o modo escuro
- Aumento do contraste nos textos de formulários (form-text) no modo escuro
- Correção da animação do botão de play na página inicial
- Adição do favicon personalizado "CC" para a identidade visual do site

## [1.1.2] - 2025-05-18

### Corrigido

- Bug na correção de legendas que adicionava textos explicativos no início e final dos arquivos SRT
- Melhoria no processamento das legendas para garantir que apenas o conteúdo SRT válido seja salvo
- Implementada detecção e remoção automática de "sujeira" nos arquivos de legendas

## [1.1.1] - 2025-05-17

### Adicionado

- Possibilidade de adicionar transcrição manual após o upload do vídeo
- Formulário dedicado na página de detalhes do vídeo para adicionar transcrição

### Melhorado

- Correção de legendas agora preserva exatamente os timestamps originais
- Melhor detecção de idioma na correção de legendas
- Tradução mais precisa para português com base na transcrição em inglês
- Feedback mais detalhado durante o processo de correção

### Corrigido

- Problema de timestamps alterados na correção de legendas
- Legendas em português incorretamente mantidas em inglês após correção

## [1.1.0] - 2025-05-15

### Adicionado

- Suporte a tema claro/escuro com detecção automática da preferência do sistema
- Toggle para alternar entre temas no menu de navegação
- Ícones intuitivos para cada modo de tema
- Persistência da preferência de tema do usuário usando localStorage

### Melhorado

- Melhor contraste de texto no tema escuro para melhor legibilidade
- Interface mais responsiva para dispositivos móveis
- Botões de ação com ícones mais descritivos
- Feedback visual aprimorado para ações do usuário

### Corrigido

- Contraste insuficiente no tema escuro em elementos de card e tabela
- Problemas de alinhamento em alguns elementos da interface
- Comportamento inconsistente em dispositivos móveis

## [1.0.0] - 2025-03-19

### Adicionado

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
- Configuração do Docker e Docker Compose
- Scripts de inicialização para ambiente com e sem Docker

### Corrigido

- Configurações de sessão para autenticação de usuários
- Layout dos botões na interface de detalhes do vídeo
- Suporte a legendas em diferentes idiomas
