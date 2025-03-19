import os
import uuid
import hashlib
import datetime
from functools import wraps
from flask import session, redirect, url_for, request, flash
from src.utils.database import execute_query

def hash_password(password):
    """Gera um hash seguro para a senha."""
    salt = os.environ.get('SALT', 'autosub_salt')
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

def verify_password(password, hashed_password):
    """Verifica se a senha fornecida corresponde ao hash armazenado."""
    return hash_password(password) == hashed_password

def create_session(user_id):
    """Cria uma nova sessão para o usuário."""
    token = str(uuid.uuid4())
    expires_at = datetime.datetime.now() + datetime.timedelta(days=1)
    
    query = """
    INSERT INTO sessions (user_id, token, expires_at)
    VALUES (%s, %s, %s)
    RETURNING id;
    """
    result = execute_query(query, params=(user_id, token, expires_at), fetchone=True)
    
    if result:
        return token
    return None

def validate_session(token):
    """Valida se a sessão é válida e não expirou."""
    if not token:
        return None
    
    query = """
    SELECT s.id, s.user_id, u.username, u.email, u.full_name, u.is_admin
    FROM sessions s
    JOIN users u ON s.user_id = u.id
    WHERE s.token = %s AND s.expires_at > NOW() AND u.is_active = TRUE;
    """
    result = execute_query(query, params=(token,), fetchone=True)
    
    if result:
        # Atualiza o tempo de expiração da sessão
        extend_query = """
        UPDATE sessions
        SET expires_at = %s
        WHERE id = %s;
        """
        new_expires_at = datetime.datetime.now() + datetime.timedelta(days=1)
        execute_query(extend_query, params=(new_expires_at, result['id']))
        
        return {
            'user_id': result['user_id'],
            'username': result['username'],
            'email': result['email'],
            'full_name': result['full_name'],
            'is_admin': result['is_admin']
        }
    
    return None

def login_required(f):
    """Decorator para rotas que exigem autenticação."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_token' not in session:
            flash('É necessário fazer login para acessar esta página.', 'error')
            return redirect(url_for('login', next=request.url))
        
        user = validate_session(session['user_token'])
        if not user:
            session.pop('user_token', None)
            flash('Sessão expirada. Por favor, faça login novamente.', 'error')
            return redirect(url_for('login', next=request.url))
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Retorna o usuário atual se estiver autenticado."""
    token = session.get('user_token')
    if token:
        return validate_session(token)
    return None

def logout_user():
    """Encerra a sessão do usuário."""
    token = session.get('user_token')
    if token:
        query = "DELETE FROM sessions WHERE token = %s;"
        execute_query(query, params=(token,))
        session.pop('user_token', None) 