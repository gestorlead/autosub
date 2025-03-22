from src.utils.database import execute_query

class UserSettings:
    def __init__(self, id=None, user_id=None, transcription_service='whisper', 
                 openai_api_key=None, openai_model='gpt-4o-mini', custom_prompt=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.transcription_service = transcription_service
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        self.custom_prompt = custom_prompt
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
                custom_prompt=result.get('custom_prompt'),
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
        
        # Se não existir, cria uma configuração padrão
        return UserSettings.create(user_id)
    
    @staticmethod
    def create(user_id, transcription_service='whisper', openai_api_key=None, 
               openai_model='gpt-4o-mini', custom_prompt=None):
        """Cria uma nova configuração para o usuário."""
        query = """
        INSERT INTO user_settings (
            user_id, transcription_service, openai_api_key, openai_model, custom_prompt
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """
        result = execute_query(
            query, 
            params=(user_id, transcription_service, openai_api_key, openai_model, custom_prompt),
            fetchone=True
        )
        
        if result:
            return UserSettings.get_by_user_id(user_id)
        return None
    
    def update(self, transcription_service=None, openai_api_key=None, 
               openai_model=None, custom_prompt=None):
        """Atualiza as configurações do usuário."""
        if transcription_service is not None:
            self.transcription_service = transcription_service
        
        if openai_api_key is not None:
            self.openai_api_key = openai_api_key
            
        if openai_model is not None:
            self.openai_model = openai_model
            
        if custom_prompt is not None:
            self.custom_prompt = custom_prompt
        
        query = """
        UPDATE user_settings 
        SET transcription_service = %s, openai_api_key = %s, 
            openai_model = %s, custom_prompt = %s, updated_at = NOW() 
        WHERE id = %s;
        """
        execute_query(query, params=(
            self.transcription_service, 
            self.openai_api_key,
            self.openai_model,
            self.custom_prompt, 
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
    def get_custom_prompt(user_id):
        """Retorna o prompt personalizado configurado para o usuário."""
        settings = UserSettings.get_by_user_id(user_id)
        return settings.custom_prompt 