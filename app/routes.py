from flask import session, render_template
from youtube import authorize, callback, try_connecting, enviar_oferta, enviar_pergunta, enviar_pedido_oracao

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

    @app.route('/enviar_oferta', methods=['POST'])
    def enviar_oferta_route():
        return enviar_oferta()

    @app.route('/enviar_pergunta', methods=['POST'])
    def enviar_pergunta_route():
        return enviar_pergunta()

    @app.route('/enviar_pedido_oracao', methods=['POST'])
    def enviar_pedido_oracao_route():
        return enviar_pedido_oracao()
