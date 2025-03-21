from src.utils.database import execute_query

class UserSettings:
    def __init__(self, id=None, user_id=None, transcription_service='autosub', 
                 openai_api_key=None, created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.transcription_service = transcription_service
        self.openai_api_key = openai_api_key
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
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
        
        # Se não existir, cria uma configuração padrão
        return UserSettings.create(user_id)
    
    @staticmethod
    def create(user_id, transcription_service='autosub', openai_api_key=None):
        """Cria uma nova configuração para o usuário."""
        query = """
        INSERT INTO user_settings (user_id, transcription_service, openai_api_key)
        VALUES (%s, %s, %s)
        RETURNING id;
        """
        result = execute_query(
            query, 
            params=(user_id, transcription_service, openai_api_key),
            fetchone=True
        )
        
        if result:
            return UserSettings.get_by_user_id(user_id)
        return None
    
    def update(self, transcription_service=None, openai_api_key=None):
        """Atualiza as configurações do usuário."""
        if transcription_service is not None:
            self.transcription_service = transcription_service
        
        if openai_api_key is not None:
            self.openai_api_key = openai_api_key
        
        query = """
        UPDATE user_settings 
        SET transcription_service = %s, openai_api_key = %s, updated_at = NOW() 
        WHERE id = %s;
        """
        execute_query(query, params=(self.transcription_service, self.openai_api_key, self.id))
        
        return True
    
    @staticmethod
    def get_transcription_service(user_id):
        """Retorna apenas o serviço de transcrição configurado para o usuário."""
        settings = UserSettings.get_by_user_id(user_id)
        return settings.transcription_service if settings else 'autosub' 