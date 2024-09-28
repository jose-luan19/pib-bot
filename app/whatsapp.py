from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os

from messages import DIZIMOS_OFERTAS

# Caminho para o seu ChromeDriver
# Configurando as opções para usar Brave
brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"  # Caminho do executável do Brave
# Obter o caminho do diretório do usuário logado no Windows
user_profile = os.getenv("USERPROFILE")
# Construir o caminho do perfil do Brave de forma dinâmica
profile_path = os.path.join(user_profile, "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data", "Default")

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = brave_path
chrome_options.add_argument(f"user-data-dir={profile_path}")  # Reutilizando o perfil do Brave
chrome_options.add_argument("--no-sandbox")  # Adiciona a flag --sandbox
chrome_options.add_argument("--disable-dev-shm-usage")  # Outras otimizações
# Cria o serviço com o caminho do ChromeDriver
base_dir = os.path.dirname(os.path.abspath(__file__))
chromedrive_path = os.path.join(base_dir, 'chromedriver', 'chromedriver.exe')

driver: WebDriver
def open_whatsapp():
     global driver, chrome_options, chromedrive_path
     # Inicializa o WebDriver com o serviço e as opções
     service = Service(chromedrive_path)  # Insira o caminho correto aqui
     driver = webdriver.Chrome(service=service, options=chrome_options)
     
     # Acessa o WhatsApp Web
     driver.get("https://web.whatsapp.com")

     # Esperar até o QR code ser escaneado e a página carregar completamente
     print("Escaneie o QR Code no WhatsApp Web.")
     time.sleep(10)
     print("Login realizado com sucesso!")

     # Buscar o grupo pelo nome
     grupo = "Arquivos"
     search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
     search_box.click()
     search_box.send_keys(grupo)
     search_box.send_keys(Keys.RETURN)

     time.sleep(2)  # Espera o grupo abrir


def envia_link_com_mensagem(link, mensagem):
     open_whatsapp()
     global driver
     message_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
     message_box.click()
     message_box.send_keys(link)
     time.sleep(8)
     message_box.send_keys(Keys.SHIFT, Keys.ENTER)
     message_box.send_keys(Keys.SHIFT, Keys.ENTER)
     message_box.send_keys(mensagem)
     message_box.send_keys(Keys.RETURN)
     # Espera um tempo antes de fechar o navegador
     time.sleep(1)

     driver.quit()

     return "Divulgação no Whatsapp enviada ", 201

def enviar_mensagem_oferta():
     open_whatsapp()
     global driver
     base_dir = os.path.dirname(os.path.abspath(__file__))
     img_path = os.path.join(base_dir, 'static', 'oferta.jpg')
     print(img_path)
     
     # Localizar o botão de anexar (clip icon) e clicar nele
     clip_button = driver.find_element(By.CSS_SELECTOR, "span[data-icon='plus']")
     clip_button.click()

     time.sleep(1)  # Aguarda o menu de anexos abrir   
     # Localizar o input de upload de arquivos e enviar o caminho da imagem
     input_anexo = WebDriverWait(driver, 10).until(
     EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
     )
     input_anexo.send_keys(os.path.abspath(img_path))

     time.sleep(2)  # Tempo para carregar a imagem
     
     # Adicionar uma mensagem de texto junto com a imagem
     message_box = driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
     message_box.send_keys(DIZIMOS_OFERTAS)

     # Enviar a imagem e o texto
     send_button = driver.find_element(By.CSS_SELECTOR, "span[data-icon='send']")
     send_button.click()
     # Espera um tempo antes de fechar o navegador
     time.sleep(3)

     driver.quit()
