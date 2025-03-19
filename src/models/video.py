import os
import datetime
from src.utils.database import execute_query

class Video:
    def __init__(self, id=None, user_id=None, title=None, description=None, original_filename=None, 
                 video_url=None, is_file=True, storage_path=None, status="pending", 
                 created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.original_filename = original_filename
        self.video_url = video_url
        self.is_file = is_file
        self.storage_path = storage_path
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def get_by_id(video_id):
        """Busca um vídeo pelo ID."""
        query = "SELECT * FROM videos WHERE id = %s;"
        result = execute_query(query, params=(video_id,), fetchone=True)
        
        if result:
            return Video(
                id=result['id'],
                user_id=result['user_id'],
                title=result['title'],
                description=result['description'],
                original_filename=result['original_filename'],
                video_url=result['video_url'],
                is_file=result['is_file'],
                storage_path=result['storage_path'],
                status=result['status'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
        return None
    
    @staticmethod
    def get_by_user(user_id, limit=None, offset=None):
        """Busca vídeos de um usuário com paginação opcional."""
        query = "SELECT * FROM videos WHERE user_id = %s ORDER BY created_at DESC"
        
        if limit is not None:
            query += f" LIMIT {limit}"
            if offset is not None:
                query += f" OFFSET {offset}"
                
        results = execute_query(query, params=(user_id,), fetchall=True)
        
        videos = []
        for result in results:
            videos.append(Video(
                id=result['id'],
                user_id=result['user_id'],
                title=result['title'],
                description=result['description'],
                original_filename=result['original_filename'],
                video_url=result['video_url'],
                is_file=result['is_file'],
                storage_path=result['storage_path'],
                status=result['status'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            ))
        
        return videos
    
    @staticmethod
    def create_from_file(user_id, title, file_path, original_filename, description=None):
        """Cria um novo vídeo a partir de um arquivo."""
        query = """
        INSERT INTO videos 
        (user_id, title, description, original_filename, is_file, storage_path, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        result = execute_query(
            query, 
            params=(user_id, title, description, original_filename, True, file_path, 'pending'),
            fetchone=True
        )
        
        if result:
            return Video.get_by_id(result['id'])
        return None
    
    @staticmethod
    def create_from_url(user_id, title, video_url, description=None):
        """Cria um novo vídeo a partir de uma URL."""
        query = """
        INSERT INTO videos 
        (user_id, title, description, video_url, is_file, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        result = execute_query(
            query, 
            params=(user_id, title, description, video_url, False, 'pending'),
            fetchone=True
        )
        
        if result:
            return Video.get_by_id(result['id'])
        return None
    
    def update_status(self, new_status):
        """Atualiza o status do vídeo."""
        query = "UPDATE videos SET status = %s, updated_at = %s WHERE id = %s;"
        now = datetime.datetime.now()
        execute_query(query, params=(new_status, now, self.id))
        self.status = new_status
        self.updated_at = now
        return True
    
    def update_storage_path(self, new_path):
        """Atualiza o caminho de armazenamento do vídeo."""
        query = "UPDATE videos SET storage_path = %s, updated_at = %s WHERE id = %s;"
        now = datetime.datetime.now()
        execute_query(query, params=(new_path, now, self.id))
        self.storage_path = new_path
        self.updated_at = now
        return True
    
    def update_details(self, title=None, description=None):
        """Atualiza os detalhes do vídeo."""
        params = []
        set_clauses = []
        
        if title and title != self.title:
            set_clauses.append("title = %s")
            params.append(title)
            self.title = title
        
        if description is not None and description != self.description:
            set_clauses.append("description = %s")
            params.append(description)
            self.description = description
        
        if not set_clauses:
            return True  # Nada para atualizar
        
        set_clauses.append("updated_at = %s")
        now = datetime.datetime.now()
        params.append(now)
        self.updated_at = now
        
        query = f"UPDATE videos SET {', '.join(set_clauses)} WHERE id = %s;"
        params.append(self.id)
        
        execute_query(query, params=params)
        return True
    
    def delete(self):
        """Exclui o vídeo e seus arquivos associados."""
        # Primeiro, excluir legendas relacionadas
        subtitles_query = "DELETE FROM subtitles WHERE video_id = %s;"
        execute_query(subtitles_query, params=(self.id,))
        
        # Em seguida, excluir o vídeo do banco de dados
        query = "DELETE FROM videos WHERE id = %s;"
        execute_query(query, params=(self.id,))
        
        # Por fim, excluir os arquivos físicos, se existirem
        if self.is_file and self.storage_path and os.path.exists(self.storage_path):
            os.remove(self.storage_path)
        
        return True
    
    def get_subtitles(self):
        """Retorna as legendas associadas ao vídeo."""
        from src.models.subtitle import Subtitle
        return Subtitle.get_by_video(self.id) 