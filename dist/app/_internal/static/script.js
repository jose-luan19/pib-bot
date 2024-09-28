let timeRemaining = 60; // Segundos para a próxima tentativa
let attempts = 1; // Contador de tentativas
let isAttempting = false; // Controla se uma tentativa está em andamento

// Função para atualizar o timer
function updateTimer() {
    if (!isAttempting) { // Só atualiza o timer se não estiver em uma tentativa
        document.getElementById('timer').innerText = timeRemaining;
        timeRemaining--;

        if (timeRemaining < 0) {
            timeRemaining = 0; // Pausa o timer quando chega a zero
            checkStatus(); // Inicia a tentativa
        }
    }
}

// Função para verificar o status (tentativa)
function checkStatus() {
    isAttempting = true; // Marca que uma tentativa está em andamento

    fetch('/check_status')
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                attempts++; // Incrementa o contador de tentativas
                document.getElementById('attempts').innerText = `${attempts}ª tentativa de 40`;
            }
        })
        .catch(error => console.error('Erro ao verificar status:', error))
        .finally(() => {
            // Libera o timer após a tentativa terminar
            isAttempting = false;
            timeRemaining = 60; // Reseta o timer após a tentativa
        });
}

setInterval(updateTimer, 1000); // Atualiza o timer a cada segundo


function toggleButtons(state) {
    document.getElementById('oferta').disabled = !state;
    document.getElementById('pergunta').disabled = !state;
    document.getElementById('oracao').disabled = !state;
}

function initializeEmojiPicker() {
    const picker = new EmojiButton();
    const emojiButton = document.querySelector('#emojiButton');
    const messageInput = document.querySelector('#messageInput');

    emojiButton.addEventListener('click', () => {
        picker.togglePicker(emojiButton);
    });

    picker.on('emoji', emoji => {
        messageInput.value += emoji;
    });
}

function enviarMensagem(url) {
    toggleButtons(false);
    let spinner = document.createElement('div');
    spinner.className = 'spinner';
    document.getElementById("space-spinner").appendChild(spinner);

    fetch(url, { method: 'POST' })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na requisição');
            }
            return response.text();
        })
        .then(data => {
            spinner.remove();
            console.log(data);
            Toastify({
                text: `${data}`,
                gravity: "bottom",
                position: 'center',
                duration: 5000,
                close: true,
                style: {
                    background: "linear-gradient(to right, #0FB070, #065BA5)",
                }
            }).showToast();
        })
        .catch(error => {
            console.error('Erro:', error);
            Toastify({
                text: `${error}`,
                gravity: "bottom",
                position: 'center',
                duration: 5000,
                close: true,
                style: {
                    background: "linear-gradient(to right, #F71616, #A12626)",
                }
            }).showToast();
        })
        .finally(() => {
            toggleButtons(true);
        });
}

function enviarMensagemWhatsapp(url) {
    document.getElementById('whatsapp').disabled = true;
    let spinner = document.createElement('div');
    spinner.className = 'spinner';
    document.getElementById("space-spinner").appendChild(spinner);

    let message = document.getElementById('messageInput');
    message = message.value ? message.value : message.placeholder
    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(message)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na requisição');
            }
            return response.text();
        })
        .then(data => {
            spinner.remove();
            console.log(data);
            Toastify({
                text: `${data}`,
                gravity: "bottom",
                position: 'center',
                duration: 5000,
                close: true,
                style: {
                    background: "linear-gradient(to right, #0FB070, #065BA5)",
                }
            }).showToast();
        })
        .catch(error => {
            console.error('Erro:', error);
            Toastify({
                text: `${error}`,
                gravity: "bottom",
                position: 'center',
                duration: 5000,
                close: true,
                style: {
                    background: "linear-gradient(to right, #F71616, #A12626)",
                }
            }).showToast();
        })
        .finally(() => {
            document.getElementById('whatsapp').disabled = false;
        });
}
