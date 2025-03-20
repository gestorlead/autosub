# Changelog

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