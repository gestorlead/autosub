from src.utils.database import execute_query

class UserSettings:
    def __init__(self, id=None, user_id=None, transcription_service='whisper', 
                 openai_api_key=None, openai_model='gpt-4o-mini', 
                 instagram_prompt=None, tiktok_prompt=None,
                 google_translate_api_key=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.transcription_service = transcription_service
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        self.instagram_prompt = instagram_prompt
        self.tiktok_prompt = tiktok_prompt
        self.google_translate_api_key = google_translate_api_key
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def get_by_user_id(user_id):
        """Busca as configurações de um usuário pelo ID."""
        query = "SELECT * FROM user_settings WHERE user_id = %s;"
        result = execute_query(query, params=(user_id,), fetchone=True)
        
        if result:
            return UserSettings(
                id=result['id'],
                user_id=result['user_id'],
                transcription_service=result['transcription_service'],
                openai_api_key=result['openai_api_key'],
                openai_model=result.get('openai_model', 'gpt-4o-mini'),
                instagram_prompt=result.get('instagram_prompt'),
                tiktok_prompt=result.get('tiktok_prompt'),
                google_translate_api_key=result.get('google_translate_api_key'),
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
        
        # Se não existir, cria uma configuração padrão
        return UserSettings.create(user_id)
    
    @staticmethod
    def create(user_id, transcription_service='whisper', openai_api_key=None, 
               openai_model='gpt-4o-mini', instagram_prompt=None, tiktok_prompt=None,
               google_translate_api_key=None):
        """Cria uma nova configuração para o usuário."""
        query = """
        INSERT INTO user_settings (
            user_id, transcription_service, openai_api_key, 
            openai_model, instagram_prompt, tiktok_prompt,
            google_translate_api_key
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        result = execute_query(
            query, 
            params=(user_id, transcription_service, openai_api_key, 
                   openai_model, instagram_prompt, tiktok_prompt,
                   google_translate_api_key),
            fetchone=True
        )
        
        if result:
            return UserSettings.get_by_user_id(user_id)
        return None
    
    def update(self, transcription_service=None, openai_api_key=None, 
               openai_model=None, instagram_prompt=None, tiktok_prompt=None,
               google_translate_api_key=None):
        """Atualiza as configurações do usuário."""
        if transcription_service is not None:
            self.transcription_service = transcription_service
        
        if openai_api_key is not None:
            self.openai_api_key = openai_api_key
            
        if openai_model is not None:
            self.openai_model = openai_model
            
        if instagram_prompt is not None:
            self.instagram_prompt = instagram_prompt
            
        if tiktok_prompt is not None:
            self.tiktok_prompt = tiktok_prompt
            
        if google_translate_api_key is not None:
            self.google_translate_api_key = google_translate_api_key
        
        query = """
        UPDATE user_settings 
        SET transcription_service = %s, openai_api_key = %s, 
            openai_model = %s, instagram_prompt = %s, tiktok_prompt = %s, 
            google_translate_api_key = %s,
            updated_at = NOW() 
        WHERE id = %s;
        """
        execute_query(query, params=(
            self.transcription_service, 
            self.openai_api_key,
            self.openai_model,
            self.instagram_prompt,
            self.tiktok_prompt,
            self.google_translate_api_key,
            self.id
        ))
        
        return True
    
    @staticmethod
    def get_transcription_service(user_id):
        """Retorna apenas o serviço de transcrição configurado para o usuário."""
        settings = UserSettings.get_by_user_id(user_id)
        return settings.transcription_service
        
    @staticmethod
    def get_openai_api_key(user_id):
        """Retorna a chave API da OpenAI do usuário."""
        settings = UserSettings.get_by_user_id(user_id)
        return settings.openai_api_key
        
    @staticmethod
    def get_openai_model(user_id):
        """Retorna o modelo OpenAI configurado para o usuário."""
        settings = UserSettings.get_by_user_id(user_id)
        return settings.openai_model
        
    @staticmethod
    def get_instagram_prompt(user_id):
        """Retorna o prompt para Instagram configurado para o usuário."""
        settings = UserSettings.get_by_user_id(user_id)
        return settings.instagram_prompt
        
    @staticmethod
    def get_tiktok_prompt(user_id):
        """Retorna o prompt para TikTok configurado para o usuário."""
        settings = UserSettings.get_by_user_id(user_id)
        return settings.tiktok_prompt
        
    @staticmethod
    def get_google_translate_api_key(user_id):
        """Retorna a chave API do Google Translate do usuário."""
        settings = UserSettings.get_by_user_id(user_id)
        return settings.google_translate_api_key 