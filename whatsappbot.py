from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import re

#Configurações
grupo_alvo = "Meu teste"
gatilho = "gap"
autor_alvo = "Pai 2"
contagem = 0
historico = set()  # Para evitar duplicatas

#Configuração do Chrome
profile_dir = os.path.join(os.getcwd(), "wpp_session")
options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("detach", True)
options.add_argument("--log-level=3")
options.add_argument(f"--user-data-dir={profile_dir}")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://web.whatsapp.com/")
print("Abra o QR code no celular e faça a leitura.")
wait = WebDriverWait(driver, 60)

#Abrir grupo
def abrir_grupo(grupo_alvo):
    campo_busca_xpath = '//div[@contenteditable="true"][@data-tab="3"]'
    campo_busca = wait.until(EC.presence_of_element_located((By.XPATH, campo_busca_xpath)))
    campo_busca.clear()
    campo_busca.click()
    campo_busca.send_keys(grupo_alvo)
    time.sleep(1)
    
    grupo = wait.until(EC.presence_of_element_located((By.XPATH, f"//span[@title='{grupo_alvo}']")))
    driver.execute_script("arguments[0].click();", grupo)
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-pre-plain-text]')))
    print(f"Grupo '{grupo_alvo}' aberto com sucesso.")

#Ler mensagens
def ler_mensagens():
    seletor = '//div[@data-pre-plain-text]'
    elementos = driver.find_elements(By.XPATH, seletor)
    registros = []
    for el in elementos:
        try:
            pre_text = el.get_attribute('data-pre-plain-text')
            match = re.search(r'\] (.*?):', pre_text)
            if not match:
                continue
            autor = match.group(1)
            texto = el.find_element(By.XPATH, './/span[contains(@class, "selectable-text")]').text
            registros.append((pre_text, autor, texto))
        except:
            continue
    return registros

#Enviar mensagem
def enviar_mensagem(texto):
    try:
        campo = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')))
        campo.click()
        campo.clear()
        campo.send_keys(texto)
        campo.send_keys(Keys.ENTER)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

#Inicialização
abrir_grupo(grupo_alvo)

#Marcar última mensagem existente
mensagens_existentes = ler_mensagens()
if mensagens_existentes:
    ultima_msg_ignoradas = mensagens_existentes[-1][0]  # apenas marcar, não processar
else:
    ultima_msg_ignoradas = None
print("Mensagens antigas ignoradas. Bot pronto para novas mensagens.")

#Monitoramento
try:
    print("--- Bot iniciado. Aguardando novas mensagens... ---")
    while True:
        mensagens = ler_mensagens()
        novas_mensagens = []

        # Pega apenas mensagens a última ignorada
        for pre_text, autor, texto in mensagens:
            if ultima_msg_ignoradas is not None and pre_text <= ultima_msg_ignoradas:
                continue
            novas_mensagens.append((pre_text, autor, texto))

        for pre_text, autor, texto in novas_mensagens:
            chave = (pre_text, texto)
            if chave not in historico:
                historico.add(chave)
                if autor.lower() == autor_alvo.lower() and gatilho.lower() in texto.lower():
                    contagem += 1
                    print(f"✅ {autor_alvo} falou '{gatilho}' ({contagem} vezes). Mensagem: '{texto}'")
                    resposta = f"{autor_alvo} Tomou Gap {contagem} vezes"
                    enviar_mensagem(resposta)

        # Atualiza a última mensagem ignorada
        if mensagens:
            ultima_msg_ignoradas = mensagens[-1][0]

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n--- Bot encerrado ---")
    print(f"Resumo: {autor_alvo} falou '{gatilho}' {contagem} vezes.")
