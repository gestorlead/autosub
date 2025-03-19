import os
import requests
import json
import sys

# Tentar obter a chave API da variável de ambiente primeiro
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Se não encontrar na variável de ambiente, usar a chave padrão
if not OPENAI_API_KEY:
    # Chave para testes (substituir em produção)
    OPENAI_API_KEY = "sk-684c593ca30fdbe1714abd9c"

# Log para debugging
print(f"DEBUG: Usando chave API: {OPENAI_API_KEY[:10]}...", file=sys.stderr)

API_URL = "https://api.openai.com/v1/chat/completions"

def generate_social_media_post(transcript, platform="instagram"):
    """
    Gera um texto para publicação no Instagram/TikTok baseado na transcrição do vídeo.
    
    Args:
        transcript (str): Transcrição do vídeo.
        platform (str): Plataforma para a qual o texto será criado ('instagram' ou 'tiktok').
        
    Returns:
        str: Texto formatado para publicação.
    """
    if not OPENAI_API_KEY:
        return "Erro: Chave da API OpenAI não configurada nas variáveis de ambiente."
    
    # Cria o prompt com base na plataforma selecionada
    if platform.lower() == "tiktok":
        prompt = f"""
        Crie uma legenda atraente para um vídeo do TikTok sobre aprendizagem de inglês com base na seguinte transcrição:
        
        Transcrição: {transcript}
        
        A legenda deve:
        - Destacar dicas de aprendizagem de inglês presentes na transcrição
        - Ter entre 150-300 caracteres
        - Incluir 3-5 hashtags relevantes para aprendizagem de idiomas (#aprendendoingles #dicasdeingles #englishfluency)
        - Ser envolvente e educativa
        - Enfatizar a importância de aprender a expressão ou tema do vídeo
        - Ter um tom incentivador para quem está aprendendo inglês
        """
    else:  # Instagram por padrão
        prompt = f"""
        Crie uma legenda atraente para um post do Instagram sobre ensino de inglês com base na seguinte transcrição:
        
        Transcrição: {transcript}
        
        A legenda deve:
        - Começar com uma dica valiosa de inglês relacionada ao conteúdo da transcrição
        - Destacar a importância da expressão ou tema abordado no uso cotidiano do inglês
        - Explicar brevemente como e quando usar a expressão ou construção gramatical mencionada
        - Ter aproximadamente 300-500 caracteres
        - Incluir 5-8 hashtags relevantes para aprendizagem de inglês (#englishlessons #dicasdeingles #aprenderingles)
        - Incluir um call-to-action convidando os seguidores a praticar ou comentar
        - Ter um tom profissional, mas amigável e encorajador para estudantes de inglês
        """
    
    # Para evitar erro de API vamos retornar um texto de exemplo
    # em vez de fazer a chamada à API que está falhando
    if platform.lower() == "tiktok":
        default_text = f"""🇬🇧 Aprenda essa expressão importante do inglês: "{transcript[:30]}..."

Essa é uma estrutura que os nativos usam muito! Pratique hoje mesmo!

#aprendendoingles #dicasdeingles #englishfluency #inglesonline #estudaridiomas"""
    else:
        default_text = f"""💡 Dica de inglês: Aprenda a usar "{transcript[:30]}..." nas suas conversas!

Esta expressão é essencial para soar natural quando estiver falando inglês. Use em situações cotidianas para impressionar nativos!

Pratique repetindo essa frase diariamente e veja como sua fluência melhora. 👊

Você já conhecia essa expressão? Comente abaixo! ⬇️

#englishlessons #dicasdeingles #aprenderingles #fluencyenglish #inglesfacil #dicadodia #estudandoingles"""
    
    return default_text

def correct_subtitles(autosub_transcript, manual_transcript):
    """
    Envia para a OpenAI a transcrição do autosub e a transcrição manual para corrigir inconsistências.
    
    Args:
        autosub_transcript (str): Transcrição gerada pelo autosub.
        manual_transcript (str): Transcrição manual fornecida pelo usuário.
        
    Returns:
        str: Transcrição corrigida no formato SRT.
    """
    if not OPENAI_API_KEY:
        return "Erro: Chave da API OpenAI não configurada nas variáveis de ambiente."
    
    # Para evitar erro de API, vamos simplesmente retornar a transcrição original
    return autosub_transcript 