import os
import re
from src.utils.database import execute_query

class Subtitle:
    def __init__(self, id=None, video_id=None, language=None, format='srt',
                 storage_path=None, created_at=None):
        self.id = id
        self.video_id = video_id
        self.language = language
        self.format = format
        self.storage_path = storage_path
        self.created_at = created_at
    
    @staticmethod
    def get_by_id(subtitle_id):
        """Busca uma legenda pelo ID."""
        query = "SELECT * FROM subtitles WHERE id = %s;"
        result = execute_query(query, params=(subtitle_id,), fetchone=True)
        
        if result:
            return Subtitle(
                id=result['id'],
                video_id=result['video_id'],
                language=result['language'],
                format=result['format'],
                storage_path=result['storage_path'],
                created_at=result['created_at']
            )
        return None
    
    @staticmethod
    def get_by_video(video_id):
        """Busca legendas de um vídeo."""
        query = "SELECT * FROM subtitles WHERE video_id = %s ORDER BY language;"
        results = execute_query(query, params=(video_id,), fetchall=True)
        
        subtitles = []
        for result in results:
            subtitles.append(Subtitle(
                id=result['id'],
                video_id=result['video_id'],
                language=result['language'],
                format=result['format'],
                storage_path=result['storage_path'],
                created_at=result['created_at']
            ))
        
        return subtitles
    
    @staticmethod
    def get_by_video_and_language(video_id, language):
        """Busca legendas de um vídeo por idioma."""
        query = "SELECT * FROM subtitles WHERE video_id = %s AND language = %s;"
        result = execute_query(query, params=(video_id, language), fetchone=True)
        
        if result:
            return Subtitle(
                id=result['id'],
                video_id=result['video_id'],
                language=result['language'],
                format=result['format'],
                storage_path=result['storage_path'],
                created_at=result['created_at']
            )
        return None
    
    @staticmethod
    def create(video_id, language, storage_path, format='srt'):
        """Cria uma nova legenda."""
        # Verificar se já existe
        existing = Subtitle.get_by_video_and_language(video_id, language)
        if existing:
            # Se já existe, atualize o caminho de armazenamento
            existing.update_storage_path(storage_path)
            return existing
        
        query = """
        INSERT INTO subtitles (video_id, language, format, storage_path)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """
        result = execute_query(
            query, 
            params=(video_id, language, format, storage_path),
            fetchone=True
        )
        
        if result:
            return Subtitle.get_by_id(result['id'])
        return None
    
    def update_storage_path(self, new_path):
        """Atualiza o caminho de armazenamento da legenda."""
        query = "UPDATE subtitles SET storage_path = %s WHERE id = %s;"
        execute_query(query, params=(new_path, self.id))
        self.storage_path = new_path
        return True
    
    def delete(self):
        """Exclui a legenda e seu arquivo físico."""
        # Primeiro, excluir o arquivo físico, se existir
        if self.storage_path and os.path.exists(self.storage_path):
            os.remove(self.storage_path)
        
        # Em seguida, excluir a legenda do banco de dados
        query = "DELETE FROM subtitles WHERE id = %s;"
        execute_query(query, params=(self.id,))
        
        return True
    
    def extract_text(self):
        """
        Extrai o texto completo do arquivo SRT, removendo os números e timestamps.
        
        Returns:
            str: Texto extraído do arquivo SRT.
        """
        if not self.storage_path or not os.path.exists(self.storage_path):
            return "Arquivo de legendas não encontrado."
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Padrão para remover números de sequência e timestamps
            # Formato SRT: número, timestamp, texto, linha em branco
            pattern = r'\d+\s*\n\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}\s*\n(.*?)\n\s*\n'
            
            # Extrai apenas as linhas de texto
            text_lines = re.findall(pattern, content + '\n\n', re.DOTALL)
            
            # Junta todas as linhas de texto
            full_text = ' '.join([line.replace('\n', ' ').strip() for line in text_lines])
            
            return full_text
        except Exception as e:
            return f"Erro ao extrair texto: {str(e)}"
            
    def update_content(self, new_content):
        """
        Atualiza o conteúdo do arquivo SRT.
        
        Args:
            new_content (str): Novo conteúdo para o arquivo SRT.
            
        Returns:
            bool: True se a operação for bem-sucedida, False caso contrário.
        """
        if not self.storage_path:
            return False
        
        try:
            # Garante que o diretório existe
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            return True
        except Exception as e:
            print(f"Erro ao atualizar arquivo SRT: {e}")
            return False
            
    def get_content(self):
        """
        Obtém o conteúdo completo do arquivo SRT.
        
        Returns:
            str: Conteúdo do arquivo SRT.
        """
        if not self.storage_path or not os.path.exists(self.storage_path):
            return "Arquivo de legendas não encontrado."
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Erro ao ler arquivo: {str(e)}"
    
    def edit_content(self, new_content):
        """
        Edita o conteúdo da legenda e atualiza o arquivo.
        
        Args:
            new_content (str): Novo conteúdo da legenda.
            
        Returns:
            bool: True se a operação for bem-sucedida, False caso contrário.
        """
        if not self.storage_path:
            return False
            
        try:
            # Cria uma cópia de backup do arquivo original
            backup_path = f"{self.storage_path}.bak"
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
            except Exception as e:
                print(f"Aviso: Não foi possível criar backup: {e}")
                
            # Atualiza o arquivo com o novo conteúdo
            with open(self.storage_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
                
            # Atualiza registro de última modificação (se aplicável)
            # query = "UPDATE subtitles SET updated_at = NOW() WHERE id = %s;"
            # execute_query(query, params=(self.id,))
            
            return True
        except Exception as e:
            print(f"Erro ao editar legenda: {e}")
            # Tenta restaurar do backup se houver erro
            try:
                if os.path.exists(backup_path):
                    with open(backup_path, 'r', encoding='utf-8') as src:
                        with open(self.storage_path, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
            except:
                pass
            return False 