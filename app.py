import os
import subprocess
from datetime import datetime
from flask import Flask, request, send_file, redirect, render_template, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
import re
from markupsafe import Markup

from src.models import User, Video, Subtitle
from src.utils import login_required, get_current_user, create_session, logout_user
from src.utils.database import check_db_connection
from src.utils.openai_helper import generate_social_media_post, correct_subtitles

# Versão do aplicativo
APP_VERSION = "1.1.3"

# Carrega as variáveis definidas no .env
load_dotenv()

# Configurações da aplicação
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/app/uploads')
ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'mp4,mov,avi,mkv').split(','))
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'sua_chave_secreta')
GOOGLE_API_KEY = os.environ.get('GOOGLE_TRANSLATE_API_KEY', '')

# Cria e configura a aplicação Flask
app = Flask(__name__, 
            template_folder='src/templates',
            static_folder='src/static')
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max upload
app.config['APP_VERSION'] = APP_VERSION
bootstrap = Bootstrap5(app)

# Filtro personalizado para converter quebras de linha em <br>
@app.template_filter('nl2br')
def nl2br(value):
    if value:
        value = str(value)
        return Markup(value.replace('\n', '<br>'))
    return value

# Cria a pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Página inicial."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.authenticate(username, password)
        if user:
            token = create_session(user.id)
            if token:
                session['user_token'] = token
                session['is_admin'] = user.is_admin
                return redirect(url_for('dashboard'))
            else:
                flash('Erro ao criar sessão. Tente novamente.', 'error')
        else:
            flash('Usuário ou senha incorretos.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Encerra a sessão do usuário."""
    logout_user()
    flash('Você saiu do sistema.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Painel do usuário com seus vídeos."""
    user = get_current_user()
    videos = Video.get_by_user(user['user_id'])
    return render_template('dashboard.html', user=user, videos=videos)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload de vídeos."""
    if request.method == 'POST':
        user = get_current_user()
        
        # Verifica se é upload de arquivo ou URL
        is_file = 'file' in request.files
        
        if is_file:
            # Upload de arquivo
            file = request.files['file']
            if file.filename == '':
                flash('Nenhum arquivo selecionado.', 'error')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                title = request.form.get('title', filename)
                description = request.form.get('description', '')
                
                # Define o caminho do arquivo
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user['user_id']))
                os.makedirs(user_folder, exist_ok=True)
                
                filepath = os.path.join(user_folder, f"{timestamp}_{filename}")
                file.save(filepath)
                
                # Cria o registro no banco de dados
                video = Video.create_from_file(
                    user['user_id'], title, filepath, filename, description
                )
                
                if video:
                    # Inicia o processamento em segundo plano (em um caso real, seria usando Celery)
                    process_video(video.id)
                    flash('Vídeo enviado com sucesso! As legendas serão geradas em breve.', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Erro ao registrar o vídeo. Tente novamente.', 'error')
            else:
                flash(f'Formato de arquivo não permitido. Use: {", ".join(ALLOWED_EXTENSIONS)}', 'error')
        else:
            # Upload por URL
            video_url = request.form.get('video_url')
            if not video_url:
                flash('URL do vídeo não fornecida.', 'error')
                return redirect(request.url)
            
            title = request.form.get('title', 'Vídeo de URL')
            description = request.form.get('description', '')
            
            # Cria o registro no banco de dados
            video = Video.create_from_url(
                user['user_id'], title, video_url, description
            )
            
            if video:
                # Inicia o processamento em segundo plano (em um caso real, seria usando Celery)
                process_video(video.id)
                flash('URL enviada com sucesso! As legendas serão geradas em breve.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Erro ao registrar o vídeo. Tente novamente.', 'error')
    
    return render_template('upload.html')

@app.route('/video/<int:video_id>')
@login_required
def video_detail(video_id):
    """Detalhe de um vídeo."""
    user = get_current_user()
    video = Video.get_by_id(video_id)
    
    if not video or video.user_id != user['user_id']:
        flash('Vídeo não encontrado ou sem permissão.', 'error')
        return redirect(url_for('dashboard'))
    
    subtitles = video.get_subtitles()
    
    # Obter texto das legendas em inglês para gerar o texto de redes sociais
    social_media_text = {}
    en_subtitle = next((s for s in subtitles if s.language == 'en'), None)
    if en_subtitle:
        transcript = en_subtitle.extract_text()
        social_media_text['instagram'] = generate_social_media_post(transcript, 'instagram')
        social_media_text['tiktok'] = generate_social_media_post(transcript, 'tiktok')
    
    return render_template('video_detail.html', video=video, subtitles=subtitles, social_media_text=social_media_text)

@app.route('/download/video/<int:video_id>')
@login_required
def download_video(video_id):
    """Download do vídeo original."""
    user = get_current_user()
    video = Video.get_by_id(video_id)
    
    if not video or video.user_id != user['user_id']:
        flash('Vídeo não encontrado ou sem permissão.', 'error')
        return redirect(url_for('dashboard'))
    
    if video.is_file and video.storage_path and os.path.exists(video.storage_path):
        return send_file(video.storage_path, as_attachment=True, download_name=video.original_filename)
    else:
        flash('Arquivo de vídeo não encontrado.', 'error')
        return redirect(url_for('video_detail', video_id=video_id))

@app.route('/download/subtitle/<int:subtitle_id>')
@login_required
def download_subtitle(subtitle_id):
    """Download de uma legenda."""
    user = get_current_user()
    subtitle = Subtitle.get_by_id(subtitle_id)
    
    if not subtitle:
        flash('Legenda não encontrada.', 'error')
        return redirect(url_for('dashboard'))
    
    video = Video.get_by_id(subtitle.video_id)
    if not video or video.user_id != user['user_id']:
        flash('Sem permissão para acessar esta legenda.', 'error')
        return redirect(url_for('dashboard'))
    
    if subtitle.storage_path and os.path.exists(subtitle.storage_path):
        filename = f"{os.path.splitext(video.original_filename)[0]}_{subtitle.language}.{subtitle.format}"
        return send_file(subtitle.storage_path, as_attachment=True, download_name=filename)
    else:
        flash('Arquivo de legenda não encontrado.', 'error')
        return redirect(url_for('video_detail', video_id=video.id))

@app.route('/profile')
@login_required
def profile():
    """Perfil do usuário."""
    user = get_current_user()
    return render_template('profile.html', user=user)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Atualiza o perfil do usuário."""
    user_data = get_current_user()
    user = User.get_by_id(user_data['user_id'])
    
    if user:
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        
        user.update(email=email, full_name=full_name)
        flash('Perfil atualizado com sucesso!', 'success')
    else:
        flash('Erro ao atualizar perfil.', 'error')
    
    return redirect(url_for('profile'))

@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """Altera a senha do usuário."""
    user_data = get_current_user()
    user = User.get_by_id(user_data['user_id'])
    
    if user:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Verificar senha atual
        auth_user = User.authenticate(user.username, current_password)
        if not auth_user:
            flash('Senha atual incorreta.', 'error')
            return redirect(url_for('profile'))
        
        # Verificar novas senhas
        if new_password != confirm_password:
            flash('As novas senhas não coincidem.', 'error')
            return redirect(url_for('profile'))
        
        # Atualizar senha
        user.change_password(new_password)
        flash('Senha alterada com sucesso!', 'success')
    else:
        flash('Erro ao alterar senha.', 'error')
    
    return redirect(url_for('profile'))

@app.route('/video/<int:video_id>/delete', methods=['POST'])
@login_required
def delete_video(video_id):
    """Exclui um vídeo."""
    user = get_current_user()
    video = Video.get_by_id(video_id)
    
    if not video or video.user_id != user['user_id']:
        flash('Vídeo não encontrado ou sem permissão.', 'error')
        return redirect(url_for('dashboard'))
    
    # Não permitir excluir vídeos em processamento
    if video.status == 'processing':
        flash('Não é possível excluir um vídeo em processamento.', 'error')
        return redirect(url_for('video_detail', video_id=video.id))
    
    # Excluir o vídeo e seus arquivos
    if video.delete():
        flash('Vídeo excluído com sucesso.', 'success')
    else:
        flash('Erro ao excluir o vídeo.', 'error')
    
    return redirect(url_for('dashboard'))

def process_video(video_id):
    """Processa um vídeo para gerar legendas."""
    video = Video.get_by_id(video_id)
    if not video:
        return
    
    video.update_status('processing')
    
    try:
        if video.is_file:
            video_path = video.storage_path
        else:
            # Download do vídeo da URL (em um caso real, seria mais robusto)
            user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(video.user_id))
            os.makedirs(user_folder, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            video_path = os.path.join(user_folder, f"{timestamp}_downloaded.mp4")
            
            subprocess.run(['youtube-dl', '-o', video_path, video.video_url], check=True)
            video.update_storage_path(video_path)
        
        # Gerar nome base para legendas
        base_path = os.path.splitext(video_path)[0]
        
        # Gerar legendas em inglês
        en_srt_path = f"{base_path}_en.srt"
        command = [
            'autosub',
            video_path,
            '-o', en_srt_path
        ]
        subprocess.run(command, check=True)
        
        # Criar registro da legenda em inglês
        Subtitle.create(video.id, 'en', en_srt_path)
        
        # Traduzir para português
        pt_srt_path = f"{base_path}_pt.srt"
        command = [
            'autosub',
            video_path,
            '-S', 'en',
            '-D', 'pt',
            '-K', GOOGLE_API_KEY,
            '-o', pt_srt_path
        ]
        subprocess.run(command, check=True)
        
        # Criar registro da legenda em português
        Subtitle.create(video.id, 'pt', pt_srt_path)
        
        video.update_status('completed')
    except Exception as e:
        print(f"Erro ao processar vídeo: {e}")
        video.update_status('error')

@app.route('/health')
def health_check():
    """Endpoint para verificação de saúde da aplicação."""
    health_status = {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "database": check_db_connection(),
        "version": APP_VERSION
    }
    
    if not health_status["database"]:
        health_status["status"] = "degraded"
        return jsonify(health_status), 500
    
    return jsonify(health_status)

@app.route('/video/<int:video_id>/correct-subtitles', methods=['POST'])
@login_required
def correct_video_subtitles(video_id):
    """Corrige as legendas usando a OpenAI com base na descrição fornecida."""
    user = get_current_user()
    video = Video.get_by_id(video_id)
    
    if not video or video.user_id != user['user_id']:
        flash('Vídeo não encontrado ou sem permissão.', 'error')
        return redirect(url_for('dashboard'))
    
    # Verificar se o vídeo tem uma descrição (transcrição manual)
    if not video.description or video.description.strip() == '':
        flash('Este vídeo não possui uma transcrição manual na descrição.', 'error')
        return redirect(url_for('video_detail', video_id=video.id))
    
    # Obter as legendas
    en_subtitle = Subtitle.get_by_video_and_language(video.id, 'en')
    pt_subtitle = Subtitle.get_by_video_and_language(video.id, 'pt')
    
    if not en_subtitle or not pt_subtitle:
        flash('Legendas não encontradas para este vídeo.', 'error')
        return redirect(url_for('video_detail', video_id=video.id))
    
    # Obter o conteúdo das legendas
    en_content = en_subtitle.get_content()
    
    # Primeiro, corrigir a legenda em inglês usando a transcrição manual
    corrected_en = correct_subtitles(en_content, video.description)
    
    # Atualizar o arquivo SRT em inglês
    en_updated = False
    if corrected_en and not corrected_en.startswith('Erro'):
        en_updated = en_subtitle.update_content(corrected_en)
        flash('Legenda em inglês corrigida com sucesso!', 'success')
    else:
        flash(f'Erro ao corrigir legenda em inglês: {corrected_en}', 'error')
    
    # Se a legenda em inglês foi atualizada com sucesso, usar ela como referência
    # para atualizar a legenda em português
    if en_updated:
        # Obter a legenda em português atual
        pt_content = pt_subtitle.get_content()
        
        # Usar a legenda em inglês corrigida como referência para a legenda em português
        corrected_pt = correct_subtitles(pt_content, corrected_en)
        
        if corrected_pt and not corrected_pt.startswith('Erro'):
            pt_subtitle.update_content(corrected_pt)
            flash('Legenda em português atualizada com base na legenda em inglês corrigida!', 'success')
        else:
            flash(f'Erro ao corrigir legenda em português: {corrected_pt}', 'error')
    else:
        flash('A legenda em português não foi atualizada porque houve um erro na correção da legenda em inglês.', 'warning')
    
    return redirect(url_for('video_detail', video_id=video.id))

@app.route('/video/<int:video_id>/generate-social', methods=['GET'])
@login_required
def generate_social_media_content(video_id):
    """Gera textos para redes sociais com base na transcrição do vídeo."""
    user = get_current_user()
    video = Video.get_by_id(video_id)
    
    if not video or video.user_id != user['user_id']:
        flash('Vídeo não encontrado ou sem permissão.', 'error')
        return redirect(url_for('dashboard'))
    
    platform = request.args.get('platform', 'instagram')
    
    # Obter a legenda em inglês
    subtitle = Subtitle.get_by_video_and_language(video.id, 'en')
    if not subtitle:
        flash('Legendas em inglês não encontradas para este vídeo.', 'error')
        return redirect(url_for('video_detail', video_id=video.id))
    
    # Extrair texto da legenda
    transcript = subtitle.extract_text()
    
    # Usar a descrição do vídeo se estiver disponível
    if video.description and video.description.strip():
        transcript = video.description
    
    # Gerar texto para rede social
    social_text = generate_social_media_post(transcript, platform)
    
    return jsonify({
        'platform': platform,
        'text': social_text
    })

@app.route('/subtitle/<int:subtitle_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_subtitle(subtitle_id):
    """Página para editar a legenda."""
    user = get_current_user()
    subtitle = Subtitle.get_by_id(subtitle_id)
    
    if not subtitle:
        flash('Legenda não encontrada.', 'error')
        return redirect(url_for('dashboard'))
    
    video = Video.get_by_id(subtitle.video_id)
    if not video or video.user_id != user['user_id']:
        flash('Sem permissão para editar esta legenda.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        new_content = request.form.get('content', '')
        if new_content:
            if subtitle.edit_content(new_content):
                flash('Legenda atualizada com sucesso!', 'success')
            else:
                flash('Erro ao atualizar legenda.', 'error')
        else:
            flash('Conteúdo vazio não é permitido.', 'error')
        return redirect(url_for('video_detail', video_id=video.id))
    
    # Método GET - exibe o formulário de edição
    content = subtitle.get_content()
    return render_template('edit_subtitle.html', 
                          video=video, 
                          subtitle=subtitle, 
                          content=content,
                          language="Inglês" if subtitle.language == "en" else "Português")

@app.route('/subtitle/<int:subtitle_id>/view', methods=['GET'])
@login_required
def view_subtitle(subtitle_id):
    """Visualiza o conteúdo da legenda."""
    user = get_current_user()
    subtitle = Subtitle.get_by_id(subtitle_id)
    
    if not subtitle:
        flash('Legenda não encontrada.', 'error')
        return redirect(url_for('dashboard'))
    
    video = Video.get_by_id(subtitle.video_id)
    if not video or video.user_id != user['user_id']:
        flash('Sem permissão para visualizar esta legenda.', 'error')
        return redirect(url_for('dashboard'))
    
    content = subtitle.get_content()
    return render_template('view_subtitle.html', 
                          video=video, 
                          subtitle=subtitle, 
                          content=content,
                          language="Inglês" if subtitle.language == "en" else "Português")

# Rotas de administração
@app.route('/admin/users')
@login_required
def admin_users():
    """Página de administração de usuários."""
    user = get_current_user()
    if not user.get('is_admin', False):
        flash('Acesso restrito a administradores.', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.get_all(active_only=False)
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    """Adiciona um novo usuário."""
    user = get_current_user()
    if not user.get('is_admin', False):
        flash('Acesso restrito a administradores.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        is_active = request.form.get('is_active') == 'on'
        is_admin = request.form.get('is_admin') == 'on'
        
        if not username or not password or not email:
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
            return redirect(url_for('admin_add_user'))
        
        new_user = User.create(username, password, email, full_name, is_active, is_admin)
        if new_user:
            flash(f'Usuário {username} criado com sucesso!', 'success')
            return redirect(url_for('admin_users'))
        else:
            flash('Erro ao criar usuário. Nome de usuário ou email já existe.', 'error')
    
    return render_template('admin_add_user.html')

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    """Edita um usuário existente."""
    current_user = get_current_user()
    if not current_user.get('is_admin', False):
        flash('Acesso restrito a administradores.', 'error')
        return redirect(url_for('dashboard'))
    
    user = User.get_by_id(user_id)
    if not user:
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('admin_users'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        is_active = request.form.get('is_active') == 'on'
        is_admin = request.form.get('is_admin') == 'on'
        
        new_password = request.form.get('password')
        
        # Atualiza dados básicos
        user.update(username, email, full_name, is_active, is_admin)
        
        # Atualiza senha se fornecida
        if new_password:
            user.change_password(new_password)
        
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin_edit_user.html', user=user)

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    """Remove um usuário."""
    user = get_current_user()
    if not user.get('is_admin', False):
        flash('Acesso restrito a administradores.', 'error')
        return redirect(url_for('dashboard'))
    
    # Evita que o usuário exclua a si mesmo
    if user_id == user['user_id']:
        flash('Você não pode excluir seu próprio usuário.', 'error')
        return redirect(url_for('admin_users'))
    
    target_user = User.get_by_id(user_id)
    if not target_user:
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('admin_users'))
    
    # Em vez de excluir, apenas desativa o usuário
    target_user.update(is_active=False)
    flash('Usuário desativado com sucesso!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/video/<int:video_id>/update-description', methods=['POST'])
@login_required
def update_video_description(video_id):
    """Atualiza a descrição (transcrição manual) de um vídeo."""
    user = get_current_user()
    video = Video.get_by_id(video_id)
    
    if not video or video.user_id != user['user_id']:
        flash('Vídeo não encontrado ou sem permissão.', 'error')
        return redirect(url_for('dashboard'))
    
    description = request.form.get('description', '').strip()
    
    if video.update_details(description=description):
        flash('Transcrição manual salva com sucesso! Agora você pode usar a função de correção de legendas.', 'success')
    else:
        flash('Erro ao salvar a transcrição manual. Tente novamente.', 'error')
    
    return redirect(url_for('video_detail', video_id=video.id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
