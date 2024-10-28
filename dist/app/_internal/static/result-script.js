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
                  console.log(data);
                  Toastify({
                        text: `${data}`,
                        gravity: "bottom",
                        position: 'center',
                        duration: 8000,
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
                        duration: 8000,
                        close: true,
                        style: {
                              background: "linear-gradient(to right, #F71616, #A12626)",
                        }
                  }).showToast();
            })
            .finally(() => {
                  spinner.remove();
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
                  console.log(data);
                  Toastify({
                        text: `${data}`,
                        gravity: "bottom",
                        position: 'center',
                        duration: 8000,
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
                        duration: 8000,
                        close: true,
                        style: {
                              background: "linear-gradient(to right, #F71616, #A12626)",
                        }
                  }).showToast();
            })
            .finally(() => {
                  spinner.remove();
                  document.getElementById('whatsapp').disabled = false;
            });
}
