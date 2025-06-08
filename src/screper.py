from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import json

# User egent aleatório, evitando a detecção do robô
ua = UserAgent(os='windows', browsers=['chrome'], min_percentage=2.0)
user_agent = str(ua.random)
        
# Definição das opções do navegador
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument(f'user-agent={user_agent}')

# Instânciação do web driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Realiza a busca da URL
driver.get('https://atpco.net/glossary/')
# Aguarda o carregamento da página
driver.implicitly_wait(10)

# Captura o elemento de seleção de registros por página
record_selector = driver.find_element(By.NAME, 'records-per-page-selector')
# Seleciona a opção "All" para exibir todos os registros
record_selector.find_element(By.XPATH, '//option[@value="All"]').click()

# Cria um dicionário para armazenar os termos do glossário
glossary_terms = {}

# Captura as opções de letra do glossário
letter_buttons = driver.find_elements(By.CLASS_NAME, 'glossary-button')
# Itera sobre cada botão de letra
for button in letter_buttons:
    # Captura o texto do botão (letra)
    letter = button.text
    # Printa a letra atual sendo processada
    print(f'Processando letra: {letter}')
    # Clica no botão da letra para carregar os termos correspondentes
    button.click()

    # Aguarda o carregamento da página
    driver.implicitly_wait(10)

    # Cria um dicionário para armazenar os termos da letra atual
    terms = {}
    # Captura os elementos dos cards de glossário
    glossary_cards = driver.find_elements(By.CLASS_NAME, 'definition-card')
    # Itera sobre cada card de glossário
    for card in glossary_cards:
        # Captura o texto do título (termo) do card
        term = card.find_element(By.CLASS_NAME, 'definition-title').text
        # Captura o texto do conteúdo da definição do card
        definition = card.find_element(By.CLASS_NAME, 'definition-main').text
        # Adiciona o termo e sua definição ao dicionário de termos
        terms[term] = {'definição': definition}

    # Adiciona os termos da letra atual ao dicionário principal
    glossary_terms[letter] = terms
    # Exibe o número total de termos coletados
    print(f'\tTermos coletados para a letra {letter}: {len(terms)}')

# Cria um arquivo JSON para armazenar os termos do glossário
glossary_terms_json = json.dumps(glossary_terms, indent=2, ensure_ascii=False)
# Salva os termos do glossário em um arquivo JSON no diretório data
with open('data/raw_data_glossary.json', 'w', encoding='utf-8') as file:
    file.write(glossary_terms_json)

# Fecha o navegador, encerrando o web driver
driver.quit()

