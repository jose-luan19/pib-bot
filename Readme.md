# Incluir Variaveis de ambiente
- CLIENT_ID
- CLIENT_SECRET
- SECRET_KEY

# Instalar o OPENSSL
[OPENSSL](https://openssl-library.org/source/index.html)

# Criar pasta static

## Gerar certificado digital
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout static/localhost-key.pem -out static/localhost.pem 