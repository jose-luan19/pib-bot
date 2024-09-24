# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['app/app.py'],  # Caminho para o script principal
    pathex=['.'],  # Caminho raiz da aplicação
    binaries=[],
    datas=[
        ('app/static/certificado_ssl.pem', 'static'),
        ('app/static/chave_privada.pem', 'static'),
        ('app/templates/result.html', 'templates'),
        ('app/templates/waiting.html', 'templates')
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app',  # Nome do executável
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True  # Define se o executável será executado no console
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app'
)
