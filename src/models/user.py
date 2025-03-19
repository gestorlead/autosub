from src.utils.database import execute_query
from src.utils.auth import hash_password, verify_password

class User:
    def __init__(self, id=None, username=None, email=None, full_name=None, is_active=True, is_admin=False, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.is_active = is_active
        self.is_admin = is_admin
        self.created_at = created_at
    
    @staticmethod
    def get_by_id(user_id):
        """Busca um usuário pelo ID."""
        query = "SELECT * FROM users WHERE id = %s;"
        result = execute_query(query, params=(user_id,), fetchone=True)
        
        if result:
            return User(
                id=result['id'],
                username=result['username'],
                email=result['email'],
                full_name=result['full_name'],
                is_active=result['is_active'],
                is_admin=result['is_admin'],
                created_at=result['created_at']
            )
        return None
    
    @staticmethod
    def get_by_username(username):
        """Busca um usuário pelo nome de usuário."""
        query = "SELECT * FROM users WHERE username = %s;"
        result = execute_query(query, params=(username,), fetchone=True)
        
        if result:
            return User(
                id=result['id'],
                username=result['username'],
                email=result['email'],
                full_name=result['full_name'],
                is_active=result['is_active'],
                is_admin=result['is_admin'],
                created_at=result['created_at']
            )
        return None
    
    @staticmethod
    def get_by_email(email):
        """Busca um usuário pelo e-mail."""
        query = "SELECT * FROM users WHERE email = %s;"
        result = execute_query(query, params=(email,), fetchone=True)
        
        if result:
            return User(
                id=result['id'],
                username=result['username'],
                email=result['email'],
                full_name=result['full_name'],
                is_active=result['is_active'],
                is_admin=result['is_admin'],
                created_at=result['created_at']
            )
        return None
    
    @staticmethod
    def authenticate(username, password):
        """Autentica um usuário pelo nome de usuário e senha."""
        query = "SELECT * FROM users WHERE username = %s;"
        result = execute_query(query, params=(username,), fetchone=True)
        
        if result and verify_password(password, result['password_hash']):
            return User(
                id=result['id'],
                username=result['username'],
                email=result['email'],
                full_name=result['full_name'],
                is_active=result['is_active'],
                is_admin=result['is_admin'],
                created_at=result['created_at']
            )
        return None
    
    @staticmethod
    def create(username, password, email, full_name=None, is_active=True, is_admin=False):
        """Cria um novo usuário."""
        # Verificar se usuário já existe
        if User.get_by_username(username) or User.get_by_email(email):
            return None
        
        password_hash = hash_password(password)
        
        query = """
        INSERT INTO users (username, password_hash, email, full_name, is_active, is_admin)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        result = execute_query(
            query, 
            params=(username, password_hash, email, full_name, is_active, is_admin),
            fetchone=True
        )
        
        if result:
            return User.get_by_id(result['id'])
        return None
    
    def update(self, username=None, email=None, full_name=None, is_active=None, is_admin=None):
        """Atualiza os dados do usuário."""
        params = []
        set_clauses = []
        
        if username and username != self.username:
            set_clauses.append("username = %s")
            params.append(username)
            self.username = username
        
        if email and email != self.email:
            set_clauses.append("email = %s")
            params.append(email)
            self.email = email
        
        if full_name is not None and full_name != self.full_name:
            set_clauses.append("full_name = %s")
            params.append(full_name)
            self.full_name = full_name
        
        if is_active is not None and is_active != self.is_active:
            set_clauses.append("is_active = %s")
            params.append(is_active)
            self.is_active = is_active
            
        if is_admin is not None and is_admin != self.is_admin:
            set_clauses.append("is_admin = %s")
            params.append(is_admin)
            self.is_admin = is_admin
        
        if not set_clauses:
            return True  # Nada para atualizar
        
        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = %s;"
        params.append(self.id)
        
        execute_query(query, params=params)
        return True
    
    def change_password(self, new_password):
        """Altera a senha do usuário."""
        password_hash = hash_password(new_password)
        query = "UPDATE users SET password_hash = %s WHERE id = %s;"
        execute_query(query, params=(password_hash, self.id))
        return True
    
    @staticmethod
    def get_all(active_only=True):
        """Retorna todos os usuários."""
        query = "SELECT * FROM users"
        if active_only:
            query += " WHERE is_active = TRUE"
        query += " ORDER BY username;"
        
        results = execute_query(query, fetchall=True)
        
        users = []
        for result in results:
            users.append(User(
                id=result['id'],
                username=result['username'],
                email=result['email'],
                full_name=result['full_name'],
                is_active=result['is_active'],
                is_admin=result['is_admin'],
                created_at=result['created_at']
            ))
        
        return users 