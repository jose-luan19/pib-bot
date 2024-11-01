import os
from flask import jsonify, request, send_from_directory, session, render_template
from youtube import try_connecting, enviar_oferta, enviar_pergunta, enviar_pedido_oracao, get_link_stream
from whatsapp import envia_link_com_mensagem, enviar_mensagem_oferta
from credentials import authorize, callback

def setup_routes(app):
    @app.route('/')
    def authorize_route():
        return authorize()

    @app.route('/callback')
    def callback_route():
        return callback()

    @app.route('/check_status')
    def check_status():
        result = try_connecting()
        if result:
            return result
        return '', 204

    @app.route('/waiting')
    def waiting():
        result = try_connecting()
        if result:
            return result
        return render_template('waiting.html')

    @app.route('/result')
    def result():
        status = session.get('status')
        return render_template('result.html', status=status)
    
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route('/enviar_oferta', methods=['POST'])
    def enviar_oferta_route():
        try:
            # enviar_mensagem_oferta() a desenvolver ainda
            return enviar_oferta()
        except Exception as ex:
            print(f'Erro ao enviar mensagem {ex}')
            return f'Erro ao enviar mensagem {ex}', 500

    @app.route('/enviar_pergunta', methods=['POST'])
    def enviar_pergunta_route():
        return enviar_pergunta()

    @app.route('/enviar_pedido_oracao', methods=['POST'])
    def enviar_pedido_oracao_route():
        return enviar_pedido_oracao()
    
    @app.route('/enviar_whatsapp', methods=['POST'])
    def enviar_divulgacao_whatsapp_route():
        link = get_link_stream()
        # Verifica se o conteúdo da requisição é JSON
        if request.is_json:
            # Obtém o payload JSON da requisição
            payload = request.get_json()
            try:
                return envia_link_com_mensagem(link, payload)
            except Exception as ex:
                print(f'Erro ao enviar mensagem {ex}')
                return f'Erro ao enviar mensagem {ex}', 500
        else:
            return jsonify({'erro': 'Formato inválido, JSON esperado'}), 400 
