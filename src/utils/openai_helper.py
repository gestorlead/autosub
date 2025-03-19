import os
import requests
import json
import sys

# Usar a chave diretamente para teste (remova isso em produção)
OPENAI_API_KEY = "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"

# Verificar se a chave está definida
print(f"DEBUG: Usando chave direta: {OPENAI_API_KEY[:10]}...", file=sys.stderr)

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
    
    # Configuração da requisição para a API da OpenAI
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Você é um professor de inglês especialista em marketing digital que cria conteúdo educativo para redes sociais focado no ensino de inglês."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        print(f"DEBUG: Enviando requisição para OpenAI API... (usando modelo gpt-4o-mini)", file=sys.stderr)
        response = requests.post(API_URL, headers=headers, data=json.dumps(data))
        print(f"DEBUG: Resposta recebida! Status: {response.status_code}", file=sys.stderr)
        if response.status_code != 200:
            print(f"DEBUG: Erro na resposta: {response.text}", file=sys.stderr)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"DEBUG: Erro na chamada à API: {str(e)}", file=sys.stderr)
        return f"Erro ao gerar texto com a API OpenAI: {str(e)}"

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
    
    prompt = f"""
    Compare a transcrição gerada automaticamente com a transcrição manual fornecida e corrija o arquivo SRT mantendo seu formato.
    
    Transcrição gerada automaticamente (formato SRT):
    {autosub_transcript}
    
    Transcrição manual correta:
    {manual_transcript}
    
    Instruções importantes:
    1. REMOVA COMPLETAMENTE os nomes de personagens (como "GRIFFIN:" ou "JET:") das legendas corrigidas
    2. Mantenha o formato exato do SRT com números de sequência e timestamps originais
    3. Substitua apenas o texto das falas para corresponder à transcrição manual correta
    4. Preserve as quebras de linha e a formatação das legendas
    5. Se a transcrição manual tiver diálogos com nomes de personagens, use apenas o texto da fala, removendo os nomes dos personagens
    6. Não adicione texto explicativo, apenas retorne o SRT corrigido
    
    Lembre-se que estamos trabalhando com conteúdo educativo para ensino de inglês, então a precisão das falas e expressões é essencial.
    """
    
    # Configuração da requisição para a API da OpenAI
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Você é um especialista em legendagem de vídeos educativos para ensino de inglês, com ampla experiência em transcrição de diálogos com múltiplos personagens."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1500
    }
    
    try:
        print(f"DEBUG: Enviando requisição para corrigir legendas... (usando modelo gpt-4o-mini)", file=sys.stderr)
        response = requests.post(API_URL, headers=headers, data=json.dumps(data))
        print(f"DEBUG: Resposta recebida para correção! Status: {response.status_code}", file=sys.stderr)
        if response.status_code != 200:
            print(f"DEBUG: Erro na resposta de correção: {response.text}", file=sys.stderr)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"DEBUG: Erro na chamada à API para correção: {str(e)}", file=sys.stderr)
        return f"Erro ao corrigir legendas com a API OpenAI: {str(e)}" 