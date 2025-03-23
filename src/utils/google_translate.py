import os
import requests
import json
import sys

def get_google_translate_api_key(user_id=None):
    """
    Obtém a chave da API do Google Translate para um usuário específico.
    
    Args:
        user_id (int, optional): ID do usuário para obter a chave personalizada.
        
    Returns:
        str: A chave da API do Google Translate configurada para o usuário ou None se não encontrada.
    """
    # Valor padrão (inicial)
    api_key = None
    
    # Tentar obter configurações do usuário
    if user_id:
        try:
            from src.models.settings import UserSettings
            api_key = UserSettings.get_google_translate_api_key(user_id)
            
            if api_key and api_key.strip():
                print(f"DEBUG: Usando chave da API Google Translate do usuário {user_id}", file=sys.stderr)
                return api_key
                
        except Exception as e:
            print(f"DEBUG: Erro ao obter chave API Google do usuário: {str(e)}", file=sys.stderr)
    
    # Se não há chave API configurada
    if not api_key:
        print("DEBUG: Nenhuma chave API do Google Translate configurada para o usuário.", file=sys.stderr)
    
    return api_key

def translate_text(text, source_lang, target_lang, user_id=None):
    """
    Traduz um texto usando a API do Google Translate.
    
    Args:
        text (str): Texto a ser traduzido.
        source_lang (str): Idioma de origem (código ISO).
        target_lang (str): Idioma de destino (código ISO).
        user_id (int, optional): ID do usuário para obter a chave personalizada.
        
    Returns:
        dict: Resposta da API com a tradução ou mensagem de erro.
    """
    # Obter a chave da API do usuário
    api_key = get_google_translate_api_key(user_id)
    
    if not api_key:
        return {
            "success": False,
            "error": "Chave da API do Google Translate não configurada. Configure sua chave nas configurações.",
            "translated_text": None
        }
    
    # URL da API do Google Translate
    url = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"
    
    # Dados para a requisição
    payload = {
        'q': text,
        'source': source_lang,
        'target': target_lang,
        'format': 'text'
    }
    
    # Cabeçalhos da requisição
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        # Realizar a requisição
        response = requests.post(url, json=payload, headers=headers)
        
        # Verificar o status da resposta
        if response.status_code == 200:
            # Extrair o texto traduzido da resposta
            data = response.json()
            translated_text = data['data']['translations'][0]['translatedText']
            
            return {
                "success": True,
                "error": None,
                "translated_text": translated_text
            }
        else:
            # Lidar com erros da API
            error_message = f"Erro na API do Google Translate: {response.status_code}"
            
            try:
                error_data = response.json()
                if 'error' in error_data and 'message' in error_data['error']:
                    error_message = error_data['error']['message']
            except:
                pass
            
            return {
                "success": False,
                "error": error_message,
                "translated_text": None
            }
            
    except Exception as e:
        # Lidar com exceções gerais
        return {
            "success": False,
            "error": f"Erro ao traduzir texto: {str(e)}",
            "translated_text": None
        } 