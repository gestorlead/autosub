import logging
import sys
import os
from datetime import datetime

# Criar diretório de logs se não existir
log_dir = '/app/logs'
os.makedirs(log_dir, exist_ok=True)

# Nome do arquivo de log com timestamp
log_file = os.path.join(log_dir, f'autosub_{datetime.now().strftime("%Y%m%d")}.log')

# Configuração do formato do log
log_format = '%(asctime)s [%(levelname)s] %(name)s - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    datefmt=date_format,
    handlers=[
        logging.StreamHandler(sys.stdout),  # Logs para stdout (terminal)
        logging.FileHandler(log_file)       # Logs para arquivo
    ]
)

# Ajustar nível de logging de bibliotecas externas para reduzir ruído
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

# Logger para uso no restante da aplicação
logger = logging.getLogger('autosub')
logger.info(f"Sistema de logs inicializado. Arquivo de log: {log_file}")
