import os
import requests
import json
import sys
import dotenv

# Carregar variáveis de ambiente dos arquivos .env ou .env.dev se existirem
dotenv.load_dotenv('.env', override=True)
if os.path.exists('.env.dev'):
    dotenv.load_dotenv('.env.dev', override=True)

# Obter as chaves da API da variável de ambiente
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# URLs das APIs
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Usar Groq por padrão se a chave estiver disponível
USE_GROQ = GROQ_API_KEY is not None and GROQ_API_KEY != ""

# Verificar qual API estamos usando
if USE_GROQ:
    print(f"DEBUG: Usando API do Groq", file=sys.stderr)
    API_KEY = GROQ_API_KEY
    API_URL = GROQ_API_URL
    MODEL = "llama3-70b-8192"  # Modelo compatível com Groq
else:
    # Verificar se a chave OpenAI está definida e exibir feedback
    if OPENAI_API_KEY:
        print(f"DEBUG: Usando API da OpenAI", file=sys.stderr)
        API_KEY = OPENAI_API_KEY
        API_URL = OPENAI_API_URL
        MODEL = "gpt-4o-mini"
    else:
        print("AVISO: Nenhuma chave de API configurada. A geração de texto não funcionará.", file=sys.stderr)
        API_KEY = ""
        API_URL = OPENAI_API_URL
        MODEL = "gpt-4o-mini"

def generate_social_media_post(transcript, platform="instagram", user_id=None):
    """
    Gera um texto para publicação no Instagram/TikTok baseado na transcrição do vídeo.
    
    Args:
        transcript (str): Transcrição do vídeo.
        platform (str): Plataforma para a qual o texto será criado ('instagram' ou 'tiktok').
        user_id (int, optional): ID do usuário para obter prompts personalizados.
        
    Returns:
        str: Texto formatado para publicação.
    """
    if not API_KEY:
        return "Erro: Chave da API não configurada."
    
    # Tentar obter prompts personalizados se o user_id for fornecido
    custom_prompt = None
    user_settings = None
    
    if user_id:
        try:
            from src.models.settings import UserSettings
            user_settings = UserSettings.get_by_user_id(user_id)
            
            if platform.lower() == "tiktok" and user_settings.tiktok_prompt:
                custom_prompt = user_settings.tiktok_prompt
            elif platform.lower() == "instagram" and user_settings.instagram_prompt:
                custom_prompt = user_settings.instagram_prompt
        except:
            # Se ocorrer erro, continua com os prompts padrão
            print("Erro ao buscar prompts personalizados, usando padrão", file=sys.stderr)
    
    # Se encontrou um prompt personalizado, usa ele substituindo o {transcript} pelo transcript real
    if custom_prompt:
        prompt = custom_prompt.replace("{transcript}", transcript)
    else:
        # Usa o prompt padrão
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
    
    # Use o modelo configurado pelo usuário, se disponível
    model = MODEL
    if user_settings and hasattr(user_settings, 'openai_model') and user_settings.openai_model:
        model = user_settings.openai_model
    
    # Configuração da requisição para a API
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Você é um professor de inglês especialista em marketing digital que cria conteúdo educativo para redes sociais focado no ensino de inglês."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        print(f"DEBUG: Enviando requisição para API... ({API_URL})", file=sys.stderr)
        response = requests.post(API_URL, headers=headers, data=json.dumps(data), timeout=30)
        print(f"DEBUG: Resposta recebida! Status: {response.status_code}", file=sys.stderr)
        
        if response.status_code != 200:
            print(f"DEBUG: Erro na resposta: {response.text}", file=sys.stderr)
            error_text = response.json().get('error', {}).get('message', 'Erro desconhecido na API')
            return f"Erro ao gerar texto (Status {response.status_code}): {error_text}"
        
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        print("DEBUG: Timeout na requisição à API", file=sys.stderr)
        return "Erro: Tempo esgotado ao tentar conectar com a API. Tente novamente mais tarde."
    except requests.exceptions.ConnectionError:
        print("DEBUG: Erro de conexão com a API", file=sys.stderr)
        return "Erro: Não foi possível conectar-se à API. Verifique sua conexão de internet."
    except Exception as e:
        print(f"DEBUG: Erro na chamada à API: {str(e)}", file=sys.stderr)
        return f"Erro ao gerar texto: {str(e)}"

def correct_subtitles(autosub_transcript, manual_transcript):
    """
    Envia para a API a transcrição do autosub e a transcrição manual para corrigir inconsistências.
    
    Args:
        autosub_transcript (str): Transcrição gerada pelo autosub.
        manual_transcript (str): Transcrição manual fornecida pelo usuário.
        
    Returns:
        str: Transcrição corrigida no formato SRT.
    """
    if not API_KEY:
        return "Erro: Chave da API não configurada."
    
    # Verifica se a transcrição é em inglês ou português
    is_english = True
    if "Qualquer" in autosub_transcript or "Você está" in autosub_transcript or "Ei" in autosub_transcript or "Você decide" in autosub_transcript:
        is_english = False
    
    if is_english:
        prompt = f"""
        Corrija o arquivo de legendas SRT gerado automaticamente com base na transcrição manual fornecida, mantendo EXATAMENTE o mesmo formato de tempo e numeração do arquivo original.

        Transcrição gerada automaticamente (formato SRT):
        {autosub_transcript}
        
        Transcrição manual correta:
        {manual_transcript}
        
        Instruções CRÍTICAS que DEVEM ser seguidas:
        1. MANTENHA EXATAMENTE os mesmos números de legenda, timestamps e formatação do arquivo original
        2. NÃO ALTERE NENHUM timestamp ou numeração do arquivo original
        3. Substitua apenas o TEXTO das falas para corresponder à transcrição manual correta
        4. Remova nomes de personagens (como "GRIFFIN:" ou "VOICE OVER:") das legendas
        5. Distribua o texto corrigido entre os mesmos segmentos de tempo da legenda original
        6. Não combine nem divida segmentos existentes
        7. Certifique-se de que o texto em cada segmento faça sentido considerando seu timestamp
        8. Mantenha o idioma em inglês
        9. IMPORTANTE: Retorne APENAS o conteúdo SRT, sem nenhum texto explicativo antes ou depois
        
        IMPORTANTE: Você deve preservar TODOS os timestamps exatamente como estão no arquivo original. 
        A principal reclamação dos usuários é que as legendas corrigidas estão com os tempos alterados.
        """
    else:
        prompt = f"""
        Traduza o arquivo de legendas SRT em português para corresponder à transcrição manual em inglês, mantendo EXATAMENTE o mesmo formato de tempo e numeração do arquivo original.
        
        Legendas em português geradas automaticamente (formato SRT):
        {autosub_transcript}
        
        Transcrição manual em inglês para referência:
        {manual_transcript}
        
        Instruções CRÍTICAS que DEVEM ser seguidas:
        1. MANTENHA EXATAMENTE os mesmos números de legenda, timestamps e formatação do arquivo original
        2. NÃO ALTERE NENHUM timestamp ou numeração do arquivo original
        3. Traduza o texto para PORTUGUÊS BRASILEIRO fluente e natural, baseando-se na transcrição manual em inglês
        4. Remova nomes de personagens (como "GRIFFIN:" ou "VOICE OVER:") das legendas traduzidas
        5. Distribua o texto traduzido entre os mesmos segmentos de tempo da legenda original
        6. Não combine nem divida segmentos existentes
        7. Certifique-se de que o texto em cada segmento faça sentido considerando seu timestamp
        8. Use português formal, mas natural, adaptando expressões idiomáticas quando necessário
        9. IMPORTANTE: Retorne APENAS o conteúdo SRT, sem nenhum texto explicativo antes ou depois
        
        IMPORTANTE: Você deve preservar TODOS os timestamps exatamente como estão no arquivo original.
        A principal reclamação dos usuários é que as legendas corrigidas estão com os tempos alterados e que as legendas em português não estão sendo traduzidas.
        """
    
    # Configuração da requisição para a API
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Você é um especialista em legendagem de vídeos educativos para ensino de inglês, com ampla experiência em transcrição de diálogos e tradução português-inglês. Sua principal responsabilidade é preservar os timestamps originais e manter o formato SRT intacto, alterando APENAS o texto das legendas. IMPORTANTE: Retorne SOMENTE o conteúdo SRT, sem explicações adicionais."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1500
    }
    
    try:
        print(f"DEBUG: Enviando requisição para corrigir legendas... ({API_URL})", file=sys.stderr)
        response = requests.post(API_URL, headers=headers, data=json.dumps(data), timeout=45)
        print(f"DEBUG: Resposta recebida para correção! Status: {response.status_code}", file=sys.stderr)
        
        if response.status_code != 200:
            print(f"DEBUG: Erro na resposta de correção: {response.text}", file=sys.stderr)
            error_text = response.json().get('error', {}).get('message', 'Erro desconhecido na API')
            return f"Erro ao corrigir legendas (Status {response.status_code}): {error_text}"
        
        result = response.json()
        corrected_content = result["choices"][0]["message"]["content"].strip()
        
        # Extrair apenas o conteúdo SRT válido, removendo texto explicativo
        # Procurar por blocos de código (delimitados por ```) que contêm o SRT
        import re
        code_pattern = r'```(?:srt)?\s*([\s\S]*?)\s*```'
        code_matches = re.findall(code_pattern, corrected_content)
        
        if code_matches:
            # Use o primeiro bloco de código encontrado
            corrected_content = code_matches[0].strip()
        else:
            # Se não encontrar blocos de código, tente identificar o conteúdo SRT pelo padrão
            srt_pattern = r'^\d+\s*\n\d{2}:\d{2}:\d{2},\d{3}\s*-->'
            if re.search(srt_pattern, corrected_content, re.MULTILINE):
                # Se encontrar padrão de SRT no início do texto, é provável que seja conteúdo SRT puro
                pass
            else:
                # Remover explicações iniciais e finais que não fazem parte do SRT
                lines = corrected_content.split('\n')
                start_idx = next((i for i, line in enumerate(lines) if re.match(r'^\d+\s*$', line)), 0)
                end_idx = len(lines)
                
                for i in range(len(lines) - 1, -1, -1):
                    if re.match(r'^\d+\s*$', lines[i]):
                        # Encontrou um número de legenda, mas verifique se é o último
                        next_line_idx = i + 1
                        if next_line_idx < len(lines) and '-->' in lines[next_line_idx]:
                            # É um número de legenda seguido por timestamp, então é parte do SRT
                            pass
                        else:
                            # Provavelmente é explicação final
                            end_idx = i
                            break
                
                corrected_content = '\n'.join(lines[start_idx:end_idx])
        
        # Validação adicional para garantir que os timestamps estão preservados
        original_lines = autosub_transcript.strip().split('\n')
        corrected_lines = corrected_content.strip().split('\n')
        
        # Se o número de linhas for muito diferente, há algo errado
        if abs(len(original_lines) - len(corrected_lines)) > 10:
            print("DEBUG: Possível problema com a correção - número de linhas muito diferente", file=sys.stderr)
            return corrected_content  # Retorna mesmo assim, para o usuário avaliar
            
        return corrected_content.strip()
    except requests.exceptions.Timeout:
        print("DEBUG: Timeout na requisição à API para correção", file=sys.stderr)
        return "Erro: Tempo esgotado ao tentar conectar com a API. Tente novamente mais tarde."
    except requests.exceptions.ConnectionError:
        print("DEBUG: Erro de conexão com a API para correção", file=sys.stderr)
        return "Erro: Não foi possível conectar-se à API. Verifique sua conexão de internet."
    except Exception as e:
        print(f"DEBUG: Erro na chamada à API para correção: {str(e)}", file=sys.stderr)
        return f"Erro ao corrigir legendas: {str(e)}" 