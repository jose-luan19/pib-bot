import os
import webbrowser
import atexit
from threading import Timer

from routes import setup_routes

from config import app, scheduler
# Configurar as rotas
setup_routes(app)

# Garantir que o scheduler será desligado corretamente
atexit.register(lambda: scheduler.shutdown())

def open_browser():
    url = 'https://127.0.0.1:443'
    webbrowser.open(url, new=2)

def run_flask():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ssl_cert_path = os.path.join(base_dir, 'static', 'certificado_ssl.pem')
    ssl_key_path = os.path.join(base_dir, 'static', 'chave_privada.pem')
    
    app.run(host='0.0.0.0', port=443, ssl_context=(ssl_cert_path, ssl_key_path))

if __name__ == "__main__":
    try:
        timer = Timer(3, open_browser)  
        timer.start()
        run_flask()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
