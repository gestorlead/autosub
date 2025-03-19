import os
import subprocess
from flask import Flask, request, send_file, redirect, flash
from flask_basicauth import BasicAuth
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Carrega as variáveis definidas no .env
load_dotenv()

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sua_chave_secreta')

# Configuração do BasicAuth utilizando variáveis de ambiente
app.config['BASIC_AUTH_USERNAME'] = os.environ.get('BASIC_AUTH_USERNAME', 'admin')
app.config['BASIC_AUTH_PASSWORD'] = os.environ.get('BASIC_AUTH_PASSWORD', 'sua_senha_forte')
app.config['BASIC_AUTH_FORCE'] = True  # Protege todas as rotas

basic_auth = BasicAuth(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo enviado.')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado.')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Recupera a chave da API do Google Translate do .env
            google_api_key = os.environ.get('GOOGLE_TRANSLATE_API_KEY', '')
            command = [
                'autosub',
                filepath,
                '-S', 'en',
                '-D', 'pt',
                '-K', google_api_key
            ]
            try:
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError:
                flash('Erro ao gerar legenda.')
                return redirect(request.url)
            
            base_name = os.path.splitext(filename)[0]
            srt_filepath = os.path.join(app.config['UPLOAD_FOLDER'], base_name + '.srt')
            
            if os.path.exists(srt_filepath):
                return send_file(srt_filepath, as_attachment=True)
            else:
                flash('Arquivo de legenda não encontrado.')
                return redirect(request.url)

    return '''
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Upload de Vídeo</title>
      </head>
      <body>
        <h1>Envie seu vídeo para gerar legenda</h1>
        <form method="post" enctype="multipart/form-data">
          <input type="file" name="file" accept="video/*">
          <input type="submit" value="Enviar">
        </form>
      </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
