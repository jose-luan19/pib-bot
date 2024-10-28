// Atualiza o timer a cada segundo 
setInterval(updateTimer, 1000);

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
    let button = document.getElementById('button-check')
    button.disabled = true
    isAttempting = true; // Marca que uma tentativa está em andamento

    fetch('/check_status')
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                attempts++; // Incrementa o contador de tentativas
                document.getElementById('attempts').innerText = `${attempts}ª tentativa de 40`;
                Toastify({
                    text: `Nenhuma transmissão online no momento`,
                    gravity: "bottom",
                    position: 'center',
                    duration: 8000,
                    close: true,
                    style: {
                        background: "linear-gradient(to right, #F71616, #A12626)",
                    }
                }).showToast();
            }
        })
        .catch(error => console.error('Erro ao verificar status:', error))
        .finally(() => {
            button.disabled = false
            // Libera o timer após a tentativa terminar
            isAttempting = false;
            timeRemaining = 60; // Reseta o timer após a tentativa
        });
}
