import re
import time
import json
import requests
import platform
import credenciais
import mysql.connector
from bs4 import BeautifulSoup
from selenium import webdriver
from mysql.connector import Error
from pyvirtualdisplay import Display
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait


def conectar_mysql(host, database, user, password, port):
    try:
        connection = mysql.connector.connect(host=host,
                                             database=database,
                                             user=user,
                                             password=password,
                                             port=port)
        if connection.is_connected():
            return connection
    except Error as e:
        print("Erro ao conectar ao MySQL", e)


def update_db(data_list):

    connection = conectar_mysql("db-webscraping.cfwkwe6mmkm5.us-east-2.rds.amazonaws.com", "db_webscraping1", "db_admin", "dbADM95WS", "3306")
    
    if connection.is_connected():
        cursor = connection.cursor()

        # Verifica se a lista de dados não está vazia
        if data_list:
            # Exclui todos os registros existentes para o site do primeiro item da lista
            query_delete = "DELETE FROM table_itens WHERE Site = %s"
            cursor.execute(query_delete, (data_list[0]['Site'],))
            connection.commit()

            # Prepara a query de inserção
            query_insert = """
                INSERT INTO table_itens (Site, Nome, Endereço, `Área Útil`, `Área Total`, Valor, `Valor da Avaliação`, `Link oferta`, `Link imagem da capa`)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Insere cada item da lista
            for data in data_list:
                valores = (data['Site'], data['Nome'], data['Endereço'], data['Área Útil'], data['Área Total'], 
                           data['Valor'], data['Valor da Avaliação'], data['Link oferta'], data['Link imagem da capa'])
                cursor.execute(query_insert, valores)
            # Confirma as mudanças
            connection.commit()
            print(f"{len(data)} valores inseridos no banco")

        cursor.close()
        connection.close()
    else:
        print("Não foi possível conectar ao banco de dados")


def get_selenium_more_visited(url):
    # Configurar o driver do Selenium
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1024, 768)

    # Abrir a página
    driver.get(url)

    # Rolar a página para carregar todo o conteúdo dinâmico
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Rolar para baixo
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Esperar o conteúdo carregar
        try:
            WebDriverWait(driver, 10).until(
                lambda driver: driver.execute_script("return document.body.scrollHeight") > last_height
                )
        except TimeoutException:
            break  # Se o tempo de espera exceder, sair do loop

        # Atualizar a altura da página após o scroll
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


    button = driver.find_element('xpath', '/html/body/app-root/div/main/div/app-home/mat-card/div[5]/app-filtro/div[1]/div[2]/button[1]')
    driver.execute_script("arguments[0].click();", button)
    time.sleep(3)

    for i in range(0, 50000, 500):
        driver.execute_script(f"window.scrollTo(0, {i});")
        time.sleep(2)  # Espera para o conteúdo carregar

    # Obter o HTML da página após o carregamento do conteúdo
    html_content = driver.page_source

    # Criar e retornar o objeto BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Fechar o driver
    driver.quit()

    return soup

class ScraperHeadless:
    def __init__(self):
        # Configurar o driver do Selenium
        self.chrome_options = Options()
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.set_window_size(1024, 768)

    def get_selenium(self, url):
        # Abrir a página
        self.driver.get(url)

        # Rolar a página para carregar todo o conteúdo dinâmico
        self.last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Rolar para baixo
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Esperar o conteúdo carregar
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: self.driver.execute_script("return document.body.scrollHeight") > self.last_height
                )
            except TimeoutException:
                break  # Se o tempo de espera exceder, sair do loop

            # Atualizar a altura da página após o scroll
            self.new_height = self.driver.execute_script("return document.body.scrollHeight")
            if self.new_height == self.last_height:
                break
            self.last_height = self.new_height

        # Obter o HTML da página após o carregamento do conteúdo
        self.html_content = self.driver.page_source

        # Criar e retornar o objeto BeautifulSoup
        soup = BeautifulSoup(self.html_content, "html.parser")
        return soup
    
    def close(self):
        # Fechar o driver
        self.driver.quit()


def get_requests(url):
    html_url = requests.get(url).text
    soup = BeautifulSoup(html_url, "html.parser")
    return soup

def chat_gpt(texto):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {credenciais.api_key}"
    }

    url_api = "https://api.openai.com/v1/chat/completions"
    id_modelo = "gpt-3.5-turbo"

    body_mensagem = {
        'model': id_modelo, 
        'messages': [{
            'role': 'user', 
            'content': f"Leia o texto '{texto}' e me responda qual a área construída, área útil, área privativa, área total, área do terreno, sua resposta deve conter apenas area_util='aqui coloca a área construída ou área útil ou área privativa, deve ser dada em metros, e conter apenas um valor, o da área que realmente tem o imóvel', area_total = 'Aqui deve conter a área total ou área do terreno, deve conter apenas um valor, o tamanho total do terreno, também em metros', e caso o texto não tenha algum nenhum dado em alguma das variáveis, você deve trocar o valor por None, e sempre responder nessa ordem e nesse formato"
        }]
    }

    body_mensagem = json.dumps(body_mensagem)

    for i in range(5):
        try:
            resposta = requests.post(url=url_api, headers=headers, data=body_mensagem)
            resposta = resposta.json()
            resposta = resposta["choices"][0]["message"]["content"]
            break

        except Exception as e:
            print(f"Erro na resposta GPT: {e}")

    if not resposta:
        resposta = [None, None]

    return resposta


# Função para extrair área útil e área total do texto
def extract_areas(text):
    area_util = None
    area_total = None

    # Padrões para extrair as áreas
    area_patterns = [
        # Padrões para área útil
        r'área útil de (\d+,\d+|\d+\.\d+|\d+) m2',
        r'área privativa de (\d+,\d+|\d+\.\d+|\d+) m2',
        r'(\d+,\d+|\d+\.\d+|\d+) m2 de área útil',
        r'(\d+,\d+|\d+\.\d+|\d+) m2 de área privativa',
        r'área útil de (\d+,\d+|\d+\.\d+|\d+) m²',
        r'área privativa de (\d+,\d+|\d+\.\d+|\d+) m²',
        r'(\d+,\d+|\d+\.\d+|\d+) m² de área útil',
        r'(\d+,\d+|\d+\.\d+|\d+) m² de área privativa',
        r'área real privativa de (\d+,\d+|\d+\.\d+|\d+) m2',
        r'área real privativa de (\d+,\d+|\d+\.\d+|\d+) m²',
        r'área própria de (\d+,\d+|\d+\.\d+|\d+) m2',
        r'área própria de (\d+,\d+|\d+\.\d+|\d+) m²',
        r'área construída de (\d+,\d+|\d+\.\d+|\d+) m2',
        r'área construída de (\d+,\d+|\d+\.\d+|\d+) m²',
        r'(\d+,\d+|\d+\.\d+|\d+) m2 de área construída',
        r'(\d+,\d+|\d+\.\d+|\d+) m² de área construída',
        r'prédio de alvenaria com a área de (\d+,\d+|\d+\.\d+|\d+) m²',
        r'prédio de alvenaria com a área de (\d+,\d+|\d+\.\d+|\d+)m²',
        r'prédio de alvenaria com a área de (\d+,\d+|\d+\.\d+|\d+) m2',
        r'prédio de alvenaria com a área de (\d+,\d+|\d+\.\d+|\d+)m2',
        
        # Padrões para área total
        r'área total de (\d+,\d+|\d+\.\d+|\d+) m2',
        r'(\d+,\d+|\d+\.\d+|\d+) m2 de área total',
        r'área total de (\d+,\d+|\d+\.\d+|\d+) m²',
        r'(\d+,\d+|\d+\.\d+|\d+) m² de área total',
        r'área real total de (\d+,\d+|\d+\.\d+|\d+) m2',
        r'área real total de (\d+,\d+|\d+\.\d+|\d+) m²',
        r'área global de (\d+,\d+|\d+\.\d+|\d+) m2',
        r'área global de (\d+,\d+|\d+\.\d+|\d+) m²',
        r'(\d+,\d+|\d+\.\d+|\d+) m2 de área global',
        r'(\d+,\d+|\d+\.\d+|\d+) m² de área global',
        r'área do terreno de (\d+,\d+|\d+\.\d+|\d+) m2',
        r'área do terreno de (\d+,\d+|\d+\.\d+|\d+) m²',
        r'(\d+,\d+|\d+\.\d+|\d+) m2 de terreno',
        r'(\d+,\d+|\d+\.\d+|\d+) m² de terreno',
        r'(\d+,\d+|\d+\.\d+|\d+) m² de área do terreno',
        r'(\d+,\d+|\d+\.\d+|\d+)m² de área do terreno',
        r'(\d+,\d+|\d+\.\d+|\d+)m2 de área do terreno',
        r'(\d+,\d+|\d+\.\d+|\d+)m2 de áreado terreno',
        r'(\d+,\d+|\d+\.\d+|\d+)m2 deárea do terreno',
        r'superfície de (\d+,\d+|\d+\.\d+|\d+) m²',
        r'superfície de (\d+,\d+|\d+\.\d+|\d+)m²',
        r'superfície de (\d+,\d+|\d+\.\d+|\d+) m2',
        r'superfície de (\d+,\d+|\d+\.\d+|\d+)m2',
    ]

    # Procurar por padrões de área útil e área total
    for pattern in area_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1).replace(',', '.'))
            if 'útil' in pattern or 'construída' in pattern or 'própria' in pattern or 'privativa' in pattern:
                if area_util is None or value < area_util:
                    area_util = float(value)
            else:
                if area_total is None or value > area_total:
                    area_total = float(value)

    return area_util, area_total

# Função modificada para obter as áreas
def get_areas(text):
    area_util, area_total = extract_areas(text)
    return [area_util, area_total]

class ScraperNoHeadless:
    def __init__(self):
        # Configurar o driver do Selenium
        self.chrome_options = Options()
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')

        if platform.system() == "Windows":
            pass
        else:
            # Iniciar o display virtual
            self.display = Display(visible=0, size=(1024, 768), backend="xvfb")
            self.display.start()

        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.set_window_size(1024, 768)


    def get_selenium_no_headless(self, url):
        # Abrir a página
        self.driver.get(url)

        time.sleep(7)

        # Obter o HTML da página após o carregamento do conteúdo
        html_content = self.driver.page_source

        # Criar e retornar o objeto BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        return soup
    
    def close(self):
        # Fechar o driver
        self.driver.quit()
