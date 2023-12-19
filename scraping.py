import os
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display
import time
import json
import credenciais

def update_db (data, site):
    pass

def get_areas (texto):
    data=[0, 0]
    return data


def get_selenium(url):
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

    # Obter o HTML da página após o carregamento do conteúdo
    html_content = driver.page_source

    # Fechar o driver
    driver.quit()

    # Criar e retornar o objeto BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    return soup

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

    # Fechar o driver
    driver.quit()

    # Criar e retornar o objeto BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    return soup


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
            'content': f'Leia o texto "{texto}" e me responda qual a área construída, área útil, área privativa, área total, área do terreno, sua resposta deve conter apenas area_util="aqui coloca a área construída ou área útil ou área privativa, deve ser dada em metros, e conter apenas um valor, o da área que realmente tem o imóvel", area_total = "Aqui deve conter a área total ou área do terreno, deve conter apenas um valor, o tamanho total do terreno, também em metros", e caso o texto não tenha algum nenhum dado em alguma das variáveis, você deve trocar o valor por None, e sempre responder nessa ordem e nesse formato'
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


def mullerleiloes():
    urls = ["https://www.mullerleiloes.com.br/lotes/imovel"]
    
    data = []
    cards = []
    for url in urls:
        soup = get_requests(url)
        links = []
        try:
            bar = soup.find("ul", class_="pagination justify-content-center")
            lis = bar.find_all("li", class_="page-item")
            numero_paginas = int(lis[-2].text)

            for x in range(numero_paginas):
                links.append(f"https://www.mullerleiloes.com.br/lotes/imovel?tipo=imovel&page={x+1}")

            for link in links:
                page = get_requests(link)
                cards_page = page.find_all("div", class_="lote")
                for card in cards_page:
                    cards.append(card)

        except:  # noqa: E722
            cards_page = soup.find_all("div", class_="lote")
            for card in cards_page:
                cards.append(card)


    for card in cards:
        img = card.find("div", class_="col-12 col-lg-2").find("a", class_="rounded").get("style")
        img = re.search(r"url\('([^']+)'\)", img)
        img_cover = img.group(1) if img else None

        name = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").find("h5").text
        
        info_div = card.find("div", class_="col-12 col-lg-7 text-justify")

        try:
            address = info_div.find("div").find("div").text.split('\n')
            for linha in address:
                if "Cidade:" in linha:
                    city1 = linha.split("Cidade:")

                    if len(city1) > 1:
                        city = city1[1].strip()
                        
                if "Endereço:" in linha:
                    address_p = linha.split("Endereço:")

                    if len(address_p) > 1:
                        address1 = address_p[1].strip().split('   ')[0]
                        break
            address = f"{address1}, {city}"
            
        except:  # noqa: E722
            address = None

        link = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").get("href")      
        soup = get_requests(link)
        
        def extrair_valor(texto):
            if texto:
                match = re.search(r'R\$([\d\.]+,\d+)', texto)
                return match.group(1) if match else None
            return None

        # Encontrar todos os elementos <h6>
        h6_elements = soup.find_all('h6', class_="text-center border-top p-2 m-0")

        # Inicializando variáveis
        appraisal_value = None
        value1 = None
        value2 = None

        # Iterar sobre os elementos encontrados
        for element in h6_elements:
            if "Valor de Avaliação:" in element.text:
                appraisal_value = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
            elif "Lance Inicial:" in element.text:
                if value1 is None:
                    value1 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
                else:
                    value2 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))

        if value1 and value2 is not None:
            value = min(value1, value2)
        
        elif value1 is not None:
            value = value1

        elif value2 is not None:
            value = value2

        else:
            value = None

        descricao = soup.find("div", class_="mb-3 p-2 border rounded text-justify").find_all("div")[1].text
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "MullerLeiloes",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link,
                        "Link imagem da capa": img_cover
                        }
        data.append(data_unit)
    return data


def lancese():
    urls = ["https://lancese.com.br/lotes/imovel"]
    data = []
    cards = []
    for url in urls:
        soup = get_requests(url)
        links = []
        try:
            bar = soup.find("ul", class_="pagination justify-content-center")
            lis = bar.find_all("li", class_="page-item")
            numero_paginas = int(lis[-2].text)

            for x in range(numero_paginas):
                links.append(f"https://lancese.com.br/lotes/imovel?tipo=imovel&page={x+1}")

            for link in links:
                page = get_requests(link)
                cards_page = page.find_all("div", class_="lote")
                for card in cards_page:
                    cards.append(card)

        except:  # noqa: E722
            cards_page = soup.find_all("div", class_="lote")
            for card in cards_page:
                cards.append(card)


    for card in cards:
        img = card.find("div", class_="col-12 col-lg-2").find("a", class_="rounded").get("style")
        img = re.search(r"url\('([^']+)'\)", img)
        img_cover = img.group(1) if img else None

        name = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").find("h5").text
        
        info_div = card.find("div", class_="col-12 col-lg-7 text-justify")

        try:
            address = info_div.find("div").find("div").text.split('\n')
            for linha in address:
                if "Cidade:" in linha:
                    city1 = linha.split("Cidade:")

                    if len(city1) > 1:
                        city = city1[1].strip()
                        
                if "Endereço:" in linha:
                    address_p = linha.split("Endereço:")

                    if len(address_p) > 1:
                        address1 = address_p[1].strip().split('   ')[0]
                        break
            address = f"{address1}, {city}"
            
        except:  # noqa: E722
            address = None

        link = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").get("href")      
        soup = get_requests(link)
        
        def extrair_valor(texto):
            if texto:
                match = re.search(r'R\$([\d\.]+,\d+)', texto)
                return match.group(1) if match else None
            return None

        # Encontrar todos os elementos <h6>
        h6_elements = soup.find_all('h6', class_="text-center border-top p-2 m-0")

        # Inicializando variáveis
        appraisal_value = None
        value1 = None
        value2 = None

        # Iterar sobre os elementos encontrados
        for element in h6_elements:
            if "Valor de Avaliação:" in element.text:
                appraisal_value = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
            elif "Lance Inicial:" in element.text:
                if value1 is None:
                    value1 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
                else:
                    value2 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))

        if value1 and value2 is not None:
            value = min(value1, value2)
        
        elif value1 is not None:
            value = value1

        elif value2 is not None:
            value = value2

        else:
            value = None

        descricao = soup.find("div", class_="mb-3 p-2 border rounded text-justify").find_all("div")[1].text
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "Lancese",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link,
                        "Link imagem da capa": img_cover
                        }
        data.append(data_unit)
    return data
    
def francoleiloes():
    soup = get_requests("https://www.francoleiloes.com.br/")

    data1_total = []
    cards1 = soup.find_all("div", "col-lg-3 col-md-6 col-sm-6 maxheight2")
    for card1 in cards1:
        img = card1.find("div", class_="imagemLeilao").get("style")
        img = re.search(r"url\('([^']+)'\)", img)
        img_cover = img.group(1) if img else None
        link = card1.find("div", class_="box_inner link-leilao with-cool-menu").get("data-link")
        data1 = {"img_cover": img_cover, "link": link}
        data1_total.append(data1)

    data = []
    for link in data1_total:
        soup = get_requests(link["link"])
        name = soup.find("div", class_="col-lg-12 col-md-12 col-sm-12 margin-bottom-20 desc").find("p").text[:100] + "..."
        address = soup.find("span", class_="primeiraLetra observations").text
                
        divs_value = soup.find("div", "col-lg-6 col-md-6 col-sm-12 col-xs-12 infoDir").find_all("span", class_="margin-top-2 weight-normal")
        for div in divs_value:
            text_div = div.find("strong")
            try:
                value0 = text_div.get_text() if text_div else None
                value0 = float(value0.split("$")[1].replace('.', '').replace(',', '.'))
            except:  # noqa: E722
                pass

            if "1º" in text_div.get_text() if text_div else None:
                value1 = value0

            elif "2º" in text_div.get_text() if text_div else None:
                value2 = value0
        
        if value1 and value2 is not None:
            value = min(value1, value2)
        
        elif value1 is not None:
            value = value1

        elif value2 is not None:
            value = value2

        else:
            value = None


        infos_area = soup.find("div", style="margin-top: 8px;")
        
        spans = infos_area.find_all("span")
        util_keywords = ["util", "construida", "útil", "construída", "privativa"]
        total_keywords = ["total", "terreno"]

        area_util = None
        area_total = None

        for span in spans:
            text = span.text.lower()
            
            # Verifica se alguma palavra em util_keywords está no texto
            if any(keyword in text for keyword in util_keywords):
                area_util = text.split(":")[1].strip()

            # Verifica se alguma palavra em total_keywords está no texto
            elif any(keyword in text for keyword in total_keywords):
                area_total = text.split(":")[1].strip()


        appraisal_value = None # O site não tem esse campo

        data_unit = {"Site": "FrancoLeiloes",
                                "Nome": name,
                                "Endereço": address,
                                "Área Útil": area_util,
                                "Área Total": area_total,
                                "Valor": value,
                                "Valor da Avaliação": appraisal_value,
                                "Link oferta": link["link"],
                                "Link imagem da capa": link["img_cover"]
                                }
        data.append(data_unit)
    return data

def leilaosantos():
    urls = ["https://leilaosantos.com.br/lotes/imovel"]

    data = []
    cards = []
    for url in urls:
        soup = get_requests(url)
        links = []
        try:
            bar = soup.find("ul", class_="pagination justify-content-center")
            lis = bar.find_all("li", class_="page-item")
            numero_paginas = int(lis[-2].text)

            for x in range(numero_paginas):
                links.append(f"https://leilaosantos.com.br/lotes/imovel?tipo=imovel&page={x+1}")

            for link in links:
                page = get_requests(link)
                cards_page = page.find_all("div", class_="lote")
                for card in cards_page:
                    cards.append(card)

        except:  # noqa: E722
            cards_page = soup.find_all("div", class_="lote")
            for card in cards_page:
                cards.append(card)


    for card in cards:
        img = card.find("div", class_="col-12 col-lg-2").find("a", class_="rounded").get("style")
        img = re.search(r"url\('([^']+)'\)", img)
        img_cover = img.group(1) if img else None

        name = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").find("h5").text
        
        info_div = card.find("div", class_="col-12 col-lg-7 text-justify")

        try:
            address = info_div.find("div").find("div").text.split('\n')
            for linha in address:
                if "Cidade:" in linha:
                    city1 = linha.split("Cidade:")

                    if len(city1) > 1:
                        city = city1[1].strip()
                        
                if "Endereço:" in linha:
                    address_p = linha.split("Endereço:")

                    if len(address_p) > 1:
                        address1 = address_p[1].strip().split('   ')[0]
                        break
            address = f"{address1}, {city}"
            
        except:  # noqa: E722
            address = None

        link = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").get("href")      
        soup = get_requests(link)
        
        def extrair_valor(texto):
            if texto:
                match = re.search(r'R\$([\d\.]+,\d+)', texto)
                return match.group(1) if match else None
            return None

        # Encontrar todos os elementos <h6>
        h6_elements = soup.find_all('h6', class_="text-center border-top p-2 m-0")

        # Inicializando variáveis
        appraisal_value = None
        value1 = None
        value2 = None

        # Iterar sobre os elementos encontrados
        for element in h6_elements:
            if "Valor de Avaliação:" in element.text:
                appraisal_value = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
            elif "Lance Inicial:" in element.text:
                if value1 is None:
                    value1 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
                else:
                    value2 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))

        if value1 and value2 is not None:
            value = min(value1, value2)
        
        elif value1 is not None:
            value = value1

        elif value2 is not None:
            value = value2

        else:
            value = None

        descricao = soup.find("div", class_="mb-3 p-2 border rounded text-justify").find_all("div")[1].text
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "LeilaoSantos",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data
            
def leiloeirobonatto():
    soup = get_requests("https://leiloeirobonatto.com/")
    cards = soup.find_all("article")[1:]

    data = []
    for card in cards:
        name = card.find("header", class_="entry-header").find("h2", class_="entry-title").find("a").text
        if "ford" in name.lower() or "veículo" in name.lower() or "carro" in name.lower() or "chevrolet" in name.lower() or "volkswagem" in name.lower() or "fiat" in name.lower():
            continue
        link = card.find("header", class_="entry-header").find("h2", class_="entry-title").find("a").get("href")
        try:
            img_cover = card.find("div", class_="post-thumbnail").find("a").find("img", class_="attachment-dara-featured-image size-dara-featured-image wp-post-image").get("src").split("?")[0]
        except:  # noqa: E722
            img_cover = None
        text = card.find("div", class_="entry-body").find("div", class_="entry-content").find("p").text.split("\n")
        
        value1 = None
        value2 = None
        for linha in text:
            if "1ª" or "1º" in linha:
                value1 = float(linha.split("$")[1].lstrip().replace('.', '').replace(',', '.'))

            elif "2ª" or "2º" in linha:
                value2 = float(linha.split("$")[1].lstrip().replace('.', '').replace(',', '.'))

        if value1 and value2 is not None:
            value = min(value1, value2)
        
        elif value1 is not None:
            value = value1

        elif value2 is not None:
            value = value2

        else:
            value = None

        soup = get_requests(link)

        address = None
        try:
            mapa_div = soup.find("div", class_="wp-block-jetpack-map")
            if mapa_div:
                data_points = mapa_div.get("data-points")
                
                # Verificando se encontrou 'data-points'
                if data_points:
                    # Carregando o JSON dos pontos de dados
                    data_points_json = json.loads(data_points)

                    # Procurando pelo endereço no JSON
                    for data_point in data_points_json:
                        if "brazil" in data_point["title"].lower() or "brasil" in data_point["title"].lower() or "rua" in data_point["title"].lower() or "avenida" in data_point["title"].lower() or "travessa" in data_point["title"].lower():
                            address = data_point["title"]

        except:  # noqa: E722
            try:
                div_content = soup.find("div", class_="entry-body").find("div", class_="entry-content")
                if not div_content:
                    return "Div de conteúdo não encontrada."

                # Encontrando todos os parágrafos dentro do div_content
                paragrafos = div_content.find_all('p')

                # Procurando pelo texto específico nos parágrafos e extraindo o endereço
                for paragrafo in paragrafos:
                    if "Visitação do Bem:" in paragrafo.text:
                        # Divide o texto na frase "Visitação do Bem:" e pega a segunda parte
                        partes = paragrafo.text.split("Visitação do Bem:")
                        if len(partes) > 1:
                            # Assume que o endereço está após a frase e antes do próximo ponto final
                            address = partes[1].split('.')[0].strip()
            except:  # noqa: E722
                address = None

        infos = soup.find("div", class_="entry-body").find("div", class_="entry-content").text.split("\n")
        for info in infos:
            if "avaliação:" in info.lower():
                appraisal_value = float(info.split("$")[1].split("(")[0].lstrip().rstrip().replace('.', '').replace(',', '.'))
     

        descricao = soup.find("div", class_="entry-body").find("div", class_="entry-content").get_text()
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "LeiloeiroBonatto",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def lessaleiloes():
    soup = get_selenium("https://www.lessaleiloes.com.br/?searchType=opened&preOrderBy=orderByFirstOpenedOffers&pageNumber=1&pageSize=30&orderBy=endDate:asc")
    cards = soup.find_all("div", class_="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-md-12 css-1ojex0")
    
    for card in cards:
        link = card.find("div", class_="react-swipeable-view-container").find("div", style="overflow: hidden;").find("a").get("href")
        link = f"https://www.lessaleiloes.com.br{link}"
        infos = card.find("div", class_="react-swipeable-view-container").find_all("div")
        for info in infos:
            hidden = info.get("aria-hidden")
            if hidden == "false":
                img_cover = info.find("div", style="overflow: hidden;").find("a").find("img").get("src")  # noqa: F841

        soup = get_selenium(link)

        name = soup.find("h1", class_="MuiTypography-root MuiTypography-h1 jss268 jss184 css-1yomz3x").text  # noqa: F841

        address = soup.find("h2", class_="MuiTypography-root MuiTypography-h2 jss183 css-1d9jgx0")  # noqa: F841
        infos = soup.find("div", class_="MuiGrid-root MuiGrid-container MuiGrid-direction-xs-column css-12g27go").find_all("span", class_="jss173").text
        for info in infos:
            if "R$" in info:
                print(info)
        texts = soup.find("div", class_="jss172").get_text().split("\n")
        for text in texts:
            if "avaliação:" in text.lower() or "atualizada:" in text.lower():
                appraisal_value = float(text.split("$").split("(").lstrip().rstrip().replace('.', '').replace(',', '.'))
            elif "segundo leilão" in text:
                value2 = float(text.split("$").split("(").lstrip().rstrip().replace('.', '').replace(',', '.'))
        print(appraisal_value)
        print(value2)
        break

def rymerleiloes():
    soup = get_requests("https://www.rymerleiloes.com.br/")
    cards = soup.find("div", class_="lista_leiloes").find_all("li")

    data = []
    for card in cards:
        img_cover = card.find("div", class_="box-img").find("div", class_="box-capa").find("img").get("src")
        link = card.find("div", class_="box-vara").find("a").get("href")
        name = card.find("div", class_="box-vara").find("a").text
        if "veículo" in name.lower() or "carro" in name.lower() or "móveis" in name.lower():
            continue
        address = card.find("section").find("div", class_="wrapp-infos-leilao").find("div", class_="col-lista-descricao").find("div", class_="descricao").find("a").text
        value1 = float(card.find("section").find("div", class_="box-info-leilao").find_all("div", class_="linha linha-praca-1 active")[1].find("span").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        
        value2 = None
        try:
            value2 = float(card.find("section").find("div", class_="box-info-leilao").find_all("div", class_="linha linha-praca-1 {M:CLASS_IS_ATIVO_2}")[1].find("span").text.split("$").lstrip().rstrip().replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            value2 = None

        if value1 and value2 is not None:
            value = min(value1, value2)
        
        elif value1 is not None:
            value = value1

        elif value2 is not None:
            value = value2

        else:
            value = None

        soup = get_requests(link)

        appraisal_value = float(soup.find("div", "col-info-lote-2").find("div", "linha-info").text.split("$")[1].lstrip().rsplit()[0].replace('.', '').replace(',', '.'))

        area_util = None
        area_total = None

        descricao = soup.find("div", class_="wrapp-detalhes-leilao").text

        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "RymerLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def grupolance():
    soup = get_requests("https://www.grupolance.com.br/imoveis")
    quant_pages = soup.find("li", class_="page-item last").find("a", class_="page-link").get("href").split("=")[1]
    
    data = []
    cards = []
    for x in range(int(quant_pages)):
        page = f"https://www.grupolance.com.br/imoveis?pagina={x+1}"
        soup = get_requests(page)
        cards_get = soup.find_all("div", class_="card-item col-sm-12 col-md-6 col-lg-4 col-xl-3")
        for card_get in cards_get:
            cards.append(card_get)

    for card in cards:
        img_cover = card.find("a", class_="card-image lazyload d-block").get("data-bg")
        img_cover = f"https:{img_cover}"
        link = card.find("a", class_="card-image lazyload d-block").get("href")
        name = card.find("a", class_="card-title").text
        values_div = card.find_all("div", class_="card-date-row")
        if len(values_div)>1:
            value1 = float(values_div[0].find("ol").find("li", class_="fs-px-12").text.split()[1].replace('.', '').replace(',', '.'))
            value2 = float(values_div[1].find("ol").find("li", class_="fs-px-12").text.split()[1].replace('.', '').replace(',', '.'))
            value = min(value1, value2)
        else:
            value = float(values_div.find("ol").find("li", class_="fs-px-12").text.split()[1].replace('.', '').replace(',', '.'))

        soup = get_requests(link)
        
        address = soup.find("div", class_="col-md-8 order-1 order-md-0").find("div", class_="mb-3").text.lstrip().rstrip()


        area_util = None
        area_total = None
        try:
            infos = soup.find("div", class_="d-flex mt-4 mb-4").find_all("div", class_="mr-4 text-center")

            try:
                area_total = infos[0].find("span", class_="d-block fs-px-16").text.split(" ")[0]

            except:  # noqa: E722
                area_total = None

            try:
                area_util = infos[1].find("span", class_="d-block fs-px-16").text.split(" ")[0]

            except:  # noqa: E722
                area_util = None
                
        except:  # noqa: E722
            try:
                infos = soup.find("div", class_="d-flex mt-4 mb-4").find("div", class_="mr-4 text-center")

                try:
                    area_total = infos.find("span", class_="d-block fs-px-16").text.split(" ")[0]

                except:  # noqa: E722
                    area_total = None
            except:  # noqa: E722
                infos = None
    

        appraisal_value = None
        try:
            appraisal_value = float(card.find("div", class_="col-md-4 order-0 order-md-1").find("div", class_="border-alt rounded p-4").find("span", style="text-decoration: line-through;").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            try:
                appraisal_value = float(card.find("div", class_="col-md-4 order-0 order-md-1").find("div", class_="border-alt rounded p-4").find("span", style="text-decoration: none;").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
            except:  # noqa: E722
                pass


        data_unit = {"Site": "GrupoLance",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def megaleiloes():
    soup = get_requests("https://www.megaleiloes.com.br/imoveis")
    number_pages = int(soup.find("li", class_="last").find("a").get("data-page"))+1

    cards = []
    for x in range(number_pages):
        link = f"https://www.megaleiloes.com.br/imoveis?pagina={x+1}"
        page = get_requests(link)
        cards_page = page.find_all("div", class_="col-sm-6 col-md-4 col-lg-3")
        for card in cards_page:
            cards.append(card)
        

    data = []
    for card in cards:
        link = card.find("div", class_="card open").find("a", class_="card-image lazyload").get("href")
        img_cover = card.find("a", class_="card-image lazyload").get("data-bg")
        name = card.find("div", class_="card-content").find("div", class_="wrap").find("a", class_="card-title").text.lstrip().rstrip()
        
        infos = card.find("div", class_="card-instance-info").find_all("div")
        if len(infos) > 2:
            value1 = float(infos[1].find("span", class_="card-instance-value").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
            value2 = float(infos[2].find("span", class_="card-instance-value").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
            value = min(value1, value2)
        else:
            value = float(infos[1].find("span", class_="card-instance-value").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
    
        soup = get_requests(link)
        
        area_util = None
        area_total = None
        try:
            infos = soup.find_all("div", style="text-align: center; display: block; margin-right: 15px;")
            for info in infos:
                text = info.text
                if "Área Útil" in text:
                    area_utils = text.split()
                    for x in area_utils:
                        try:
                            area_util = float(x.split("l")[1])
                            break
                        except:  # noqa: E722
                            pass

                if "Área Total" in text:
                    area_totals = text.split()
                    for y in area_totals:
                        try:
                            area_total = float(y)
                            break
                        except:  # noqa: E722
                            pass
        
        except:  # noqa: E722
            pass

        if area_util is None or area_total is None:
            texts = soup.find_all("div", style="text-align: center; display: block; margin-right: 15px;")
            texts_list = []

            for text in texts:
                texts_list.append(text.text)

            descricao = ", ".join(texts_list)
            areas = get_areas(descricao)

            area_util = areas[0]
            area_total = areas[1]

        address = soup.find("div", class_="locality item").find("div", class_="value").text.lstrip().rstrip()
        appraisal_value = float(soup.find("div", class_="rating-value").find("div", class_="value").text.split("$")[1].split("(")[0].lstrip().rstrip().replace('.', '').replace(',', '.'))

        data_unit = {"Site": "MegaLeiloes",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link,
                        "Link imagem da capa": img_cover
                        }
        data.append(data_unit)
    return data

def vivaleiloes():
    urls = ["https://www.vivaleiloes.com.br/busca/#Engine=Start&Pagina=1&Busca=&Mapa=&ID_Categoria=55&PaginaIndex=1&QtdPorPagina=99999"]

    cards = []
    for url in urls:
        soup = get_selenium(url)
        cards_page = soup.find_all("div", class_="col-xs-12 col-sm-6 col-md-4 col-lg-3 dg-leiloes-item-col")
        for card in cards_page:
            cards.append(card)
    
    data = []
    for card in cards:
        link = card.find("div", class_="dg-leiloes-lista-img").find("a", class_="dg-leiloes-img").get("href")
        img_cover = card.find("div", class_="dg-leiloes-lista-img").find("a", class_="dg-leiloes-img").find("span").get("style").split("(")[1].split(")")[0]
        name = card.find("span", class_="dg-leiloes-nome-leilao").text

        value1, value2, value = None, None, None

        # Encontre os valores das praças
        value1_span = card.find("div", class_="dg-leiloes-data BoxPracas").find('span', class_='ValorMinimoLancePrimeiraPraca')
        value2_span = card.find("div", class_="dg-leiloes-data BoxPracas").find('span', class_='ValorMinimoLanceSegundaPraca')

        # Extraia os valores, se existirem
        if value1_span:
            value1 = value1_span.get_text(strip=True)

        if value2_span:
            value2 = value2_span.get_text(strip=True)

        # Aplique a lógica para definir 'value'
        if value1 and value2:
            # Converte os valores para float para comparação
            num_value1 = float(value1.replace('R$ ', '').replace('.', '').replace(',', '.'))
            num_value2 = float(value2.replace('R$ ', '').replace('.', '').replace(',', '.'))
            value = min(num_value1, num_value2)
        elif value1:
            value = value1

        appraisal_value = float(card.find("div", class_="dg-leiloes-valor-avaliacao").find("strong").text.split("$")[1].lstrip().split()[0].replace('.', '').replace(',', '.'))

        card = get_requests(link)
        
        address = card.find("section", class_="dg-lote-box dg-lote-local").find("div", class_="dg-lote-local-endereco").text.lstrip().rstrip()

        area_util = None
        area_total = None
        d = []
        descricao = ""

        descs = card.find("div", class_="dg-lote-descricao-txt").find_all("span", style="font-family:Arial,Helvetica,sans-serif")
        for desc in descs:
            d.append(desc.text)

        descricao = "; ".join(d)

        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]
        
        data_unit = {"Site": "VivaLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def biasileiloes():
    soup = get_selenium("https://www.biasileiloes.com.br/lotes/todas-categorias/pesquisa?pagina=1")
    quant_pages = soup.find("span", class_="text-paging").find("span", "total-page").text
    
    cards = []
    for x in range(int(quant_pages)):
        link = f"https://www.biasileiloes.com.br/lotes/todas-categorias/pesquisa?pagina={x+1}"
        soup = get_selenium(link)
        cards_page = soup.find_all("div", class_="col-xs-12 col-sm-6 col-md-4 col-lg-3")
        for card_page in cards_page:
            cards.append(card_page)

    data = []
    for card in cards:
        img_cover = card.find("div", class_="photo-lot").find("img").get("src")
        link = card.find("a", class_="item-photo").get("href")
        link = f"https://www.biasileiloes.com.br{link}"
        name = card.find("div", class_="photo-text").text.replace("\n", "")
        
        value1, value2, value = None, None, None
        values = card.find("div", class_="col-xl-12")
        try:
            value1 = float(values.find("div").text.split("$")[1].replace("\n", "").replace('.', '').replace(',', '.'))
            value2 = float(values.find("span", class_="price-line-2-pracas").text.split("$")[1].replace("\n", "").replace('.', '').replace(',', '.'))
            value = min(value1, value2)
        except:  # noqa: E722
            value = float(values.find("span", class_="price-line").text.split("$")[1].replace("\n", "").replace('.', '').replace(',', '.'))
        
        soup = get_selenium(link)
        address = soup.find("span", class_="lot-subtitle").text.lstrip().rstrip()

        descricao = soup.find("div", class_="col-lg-12").find("div", class_="panel panel-default").get_text(strip=True)

        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        appraisal_value = None #site não tem o campo

        data_unit = {"Site": "VivaLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def sanchesleiloes():
    soup = get_requests("https://sanchesleiloes.com.br/externo/")
    cards = soup.find_all("div", class_="col-12 col-sm-6 col-md-4 col-lg-3 mb-4 py-0 px-1")

    data = []
    for card in cards:
        link = card.find("div", class_="card-bem-wrap").find("a").get("href")
        link = f"https://sanchesleiloes.com.br{link}"

        name = card.find("div", class_="card-bem-descricao").find("p").text
        if "bens" in name.lower() or "veículos" in name.lower() or "veículo" in name.lower() or "diversos" in name.lower():
            continue
        img_cover = card.find("div", class_="carousel-item active h-100").find("img", class_="card-bem-img h-100").get("src")
        value = float(card.find("div", class_="bem-info").find("p", class_="float-right").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        soup = get_requests(link)

        address = soup.find("div", class_="col-12 col-sm-8 col-md-9 my-1 mt-md-4 mt-xl-2").find_all("div", class_="col-12")[-1].text.split(":")[1].lstrip().rstrip()

        appraisal_value = float(soup.find("div", class_="col-12 col-md-10 col-lg-6 mb-3 pl-lg-5").find("p", class_="mb-0 destaque").text.split(":")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        try:
            descricao = soup.find("div", class_="col-8 py-3").find("p").find("p").text
            areas = get_areas(descricao)

            area_util = areas[0]
            area_total = areas[1]
        except:  # noqa: E722
            area_util = None
            area_total = None

        data_unit = {"Site": "SanchesLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def grandesleiloes():
    soup = get_requests("https://www.grandesleiloes.com.br/leilao/lotes/imoveis")
    linhas = soup.find_all("div", class_="row")

    cards = []
    for linha in linhas:
        xs = linha.find_all("div", class_="col-12 col-sm-4 col-xl-3")
        for x in xs:
            cards.append(x)
    
    data = []
    for card in cards:
        name = card.find("div", class_="card-body").find("h4", class_="card-title card-title-leilao text-center").text.lstrip().rstrip()
        link = card.find("div", class_="card-header card-header-image").find("a").get("href")
        img_cover = card.find("div", class_="card-header card-header-image").find("a").find("img").get("src")

        soup = get_requests(link)

        descricao = None
        try:
            descricao = soup.find("div", class_="card card-nav-tabs").find("div", class_="card-body").find("p", style="margin-right:-5px; text-align:justify").text
            areas = get_areas(descricao)

            area_util = areas[0]
            area_total = areas[1]
        except:  # noqa: E722
            area_util = None
            area_total = None
        
        soup = get_requests(f"https://www.grandesleiloes.com.br{soup.find("a", class_="btn btn-primary btn-round btn-block").get("href")}")

        try:
            infos = soup.find_all("div", class_="row")
            for info in infos:
                info = info.text
                if "LEILÃO:" in info:
                    xs = info.split("\n")
                    for x in xs:
                        if "LEILÃO: LEILÃO" in x:
                            address = x.split("EM")[1].lstrip().rstrip()
        except:  # noqa: E722
            address = None

        appraisal_value = float(soup.find_all("div", class_="card-body")[-2].find("h4").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        value = float(soup.find("p", class_="lance-inicial-valor").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))


        data_unit = {"Site": "GrandesLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def lancecertoleiloes():
    urls = ["https://www.lancecertoleiloes.com.br/filtro/imoveis"]
    cards = []
    for url in urls:
        soup = get_requests(url)
        numero_paginas = 1
        try:
            numero_paginas = int(soup.find("ul", id="ContentPlaceHolder1_rl_leilao_pagination").find_all("li")[-2].text)
        except:  # noqa: E722
            numero_paginas = 1

        for page in range(numero_paginas):
            soup = get_requests(f"{url}?pag={page}")
            cards_page = soup.find_all("div", class_="col-md-3 btn-leilao")
            for card in cards_page:
                cards.append(card)

    data = []
    for card in cards:
        name = card.find("div", class_="lote-detalhes").find("div", class_="lote-descricao").text.lstrip().rstrip().replace("\r\n", " ")
        link = f"https://www.lancecertoleiloes.com.br{card.find("a").get("href").replace("..", "")}"
        img_cover = card.find("img", class_="lote-img").get("src")
        
        soup = get_requests(link)
        value = float(soup.find("span", id="ContentPlaceHolder1_lblLanceinicial").text.split()[0].replace('.', '').replace(',', '.'))
        appraisal_value = None
        try:
            appraisal_value = float(soup.find("span", id="ContentPlaceHolder1_lblAvaliacao").text.replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            pass
        
        address = None
        try:
            address = f"{soup.find("span", id="ContentPlaceHolder1_lblEndereco").text}, de {soup.find("span", id="ContentPlaceHolder1_lblCidade").text}, em {soup.find("span", id="ContentPlaceHolder1_lblEstado").text}"
        except:  # noqa: E722
            pass

        descricao = None
        try:
            descricao = soup.find("span", id="ContentPlaceHolder1_lblDescricaoImovel").text
            areas = get_areas(descricao)

            area_util = areas[0]
            area_total = areas[1]
        except:  # noqa: E722
            area_util = None
            area_total = None
        
        data_unit = {"Site": "LancecertoLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def hastapublica():
    urls = ["https://www.hastapublica.lel.br/leilao/lotes/imoveis"]
    cards = []
    for url in urls:
        soup = get_requests(url)
        cards_page = soup.find_all("div", class_="col-12 col-md-6 col-lg-4 col-xl-3")
        for card in cards_page:
            cards.append(card)

    data = []
    for card in cards:
        try:
            link = card.find("div", class_="back").find("div", class_="card-footer").find("a").get("href")
            link = f"https://www.hastapublica.lel.br{link}"
            img_cover = card.find("div", class_="front").find("div", class_="carousel-inner").find("img").get("src")
        except:  # noqa: E722
            try:
                link = card.find("div", class_="card-header card-header-image").find("a").get("href")
                link = f"https://www.hastapublica.lel.br{link}"
                img_cover = card.find("div", class_="card-header card-header-image").find("a").find("img").get("src")
            except:  # noqa: E722
                link = card.find("a", class_="btn btn-link btn-block").get("href")
                link = f"https://www.hastapublica.lel.br{link}"
                img_cover = "https://www.hastapublica.lel.br/build/images/nopicture.png"

        soup = get_requests(link)
        name = soup.find("h4", class_="card-title").text
        address = None #site não tem esse campo, tendo apenas no título
        appraisal_value = None
        try:
            appraisal_value = float(soup.find("div", class_="card-body text-center").find("h4").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            pass
        value = float(soup.find("p", class_="lance-inicial-valor").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        descricao = None
        try:
            descricao = soup.find("div", class_="col-12 descricao").text.replace("\n", " ").lstrip().rstrip()
            areas = get_areas(descricao)

            area_util = areas[0]
            area_total = areas[1]
        except:  # noqa: E722
            area_util = None
            area_total = None

        data_unit = {"Site": "HastaPublica",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def leiloes123():
    urls = ["https://www.123leiloes.com.br/subcategorias/apartamentos", "https://www.123leiloes.com.br/subcategorias/vagas-de-garagem", "https://www.123leiloes.com.br/subcategorias/imovel-rural", "https://www.123leiloes.com.br/subcategorias/casa", "https://www.123leiloes.com.br/subcategorias/fazenda", "https://www.123leiloes.com.br/subcategorias/galpao"]
    cards = []
    for url in urls:
        soup = get_requests(url)
        cards_page = soup.find_all("div", class_="col-xl-3 col-lg-4 col-md-6")
        for card in cards_page:
            cards.append(card)
    data = []
    for card in cards:
        name = card.find("div", class_="d-block border mb-2 hv-1 hvr-underline-from-left").find("a").get("title")
        link = card.find("div", class_="d-block border mb-2 hv-1 hvr-underline-from-left").find_all("a")[-1].get("href")
        link = f"https://www.123leiloes.com.br/{link}"
        img_cover = card.find("div", class_="d-block border mb-2 hv-1 hvr-underline-from-left").find("div", class_="leilao-banner").get("style").split("(")[1].split(")")[0]
        img_cover = f"https://www.123leiloes.com.br/{link}"

        value = None
        pracas = card.find("div", class_="leilao-pracas border-bottom").find_all("div")
        if len(pracas) > 1:
            try:
                value1 = float(pracas[0].text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
                value2 = float(pracas[1].text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
                value = min(value1, value2)
            except:  # noqa: E722
                pass
        elif len(pracas) == 1:
            try:
                value = float(int(pracas[0].text.split("$")[1].lstrip().rstrip()).replace('.', '').replace(',', '.'))
            except:  # noqa: E722
                value = float(pracas[0].text.replace('.', '').replace(',', '.'))

        time.sleep(0.05)
        soup = get_requests(link)
        
        area_util = None
        area_total = None 
        address = None      
        try:
            descricao = soup.find("div", class_="card-body pt-2 pb-0 px-3 text-secondary").find("article", class_="d-block").text
            areas = get_areas(descricao)

            area_util = areas[0]
            area_total = areas[1]
        
            descricao2 = descricao.split("\n")
            for linha in descricao2:
                if "endereço onde" in linha.lower():
                    descxs = linha.split(":")
                    for index, desc in enumerate(descxs):
                        if "situado" in desc:
                            address = descxs[index+1].lstrip().rstrip()
        except:  # noqa: E722
            pass

        appraisal_value = None
        try:
            linhas = soup.find("div", class_="card-body p-2 text-secondary text-center small").text.split("\n")
            for linha in linhas:
                if "avaliação:" in linha.lower():
                    appraisal_value = float(linha.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            pass

        data_unit = {"Site": "123Leiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def moraesleiloes():
    soup = get_requests("https://www.moraesleiloes.com.br/lotes/imovel")
    cards = soup.find_all("div", class_="lote")
    
    data = []
    for card in cards:
        name = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").find("h5").text
        infos = card.find("a", class_="rounded").get("style").split()
        for info in infos:
            if "url(" in info:
                img_cover = info.split("(")[1].split(")")[0]
        link = card.find("a", class_="rounded").get("href")

        soup = get_requests(link)
        address = soup.find("div", class_="mb-3 p-2 border rounded").text.replace("\n", " ").replace("Endereço:", "").replace("Cidade:", "em").replace("CEP:", "CEP nº").lstrip().rstrip()
        
        while "  " in address:
            address = address.replace("  ", " ")
        
        value1 = None
        value2 = None
        values = soup.find_all("h6", class_="text-center border-top p-2 m-0")
        for x in values:
            if "$" in x.text:
                if value1 is None:
                    value1 = float(x.text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
                elif value1 is not None and value2 is None:
                    value2 = float(x.text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        if value1 is not None and value2 is not None:
            value = min(value1, value2)
        elif value1 is not None and value2 is None:
            value = value1
        else:
            value = None

        
        descricao = soup.find("div", class_="mb-3 p-2 border rounded text-justify").text
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        appraisal_value = None #Site não tem o campo

        data_unit = {"Site": "MoraesLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def oleiloes():
    soup = get_requests("https://oleiloes.com.br/")
    cards = soup.find_all("div", class_="group m-2 mb-2 rounded-md border-[1px] bg-white shadow-sm shadow-zinc-100 transition-all ease-in hover:shadow-2xl dark:border-zinc-800 dark:bg-gradient-to-t dark:from-zinc-900 dark:to-zinc-900 dark:shadow-zinc-900 md:m-0")

    data = []
    for card in cards:
        name = card.find("a", class_="font-bold text-site-box-titulo dark:text-site-box-titulo-dark").text.replace("\n", "").lstrip().rstrip()
        if "sofá" in name.lower() or "perfil" in name.lower() or "veículo" in name.lower() or "veiculo" in name.lower() or "moinho" in name.lower() or "piso" in name.lower() or "joias" in name.lower() or "jóias" in name.lower() or "mercedes" in name.lower() or "impressora" in name.lower() or "som" in name.lower() or "aparelho" in name.lower() or "caminhão" in name.lower() or "carro" in name.lower() or "engerauto" in name.lower():
            continue
        link = card.find("a", class_="font-bold text-site-box-titulo dark:text-site-box-titulo-dark").get("href")
        address = card.find("div", class_="my-4 flex h-auto items-center justify-center px-4 text-sm text-zinc-500 dark:text-zinc-400 md:h-14").find("div", class_="flex-1 text-center").find("div", class_="mb-2").find("p").text.lstrip().rstrip()
        img_cover = card.find("div", class_="relative h-52 overflow-hidden rounded-t-md").find("img").get("src")

        soup = get_requests(link)
        appraisal_value = float(soup.find("tbody").find_all("tr", class_="odd:bg-white even:bg-zinc-50 dark:text-zinc-300 dark:odd:bg-zinc-700 dark:even:bg-zinc-800")[2].find("td", class_="py-3 px-4").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        infos = soup.find("tbody").find_all("tr", class_="odd:bg-white even:bg-zinc-50 dark:text-zinc-300 dark:odd:bg-zinc-700 dark:even:bg-zinc-800")[3].find("td", class_="py-3 px-4").find_all("span")
        if len(infos) > 1:
            value1 = float(infos[0].text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
            value2 = float(infos[2].text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
            value = min(value1, value2)

        elif len(infos) == 1:
            value = float(infos[0].text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        descricao = soup.find("div", class_="py-2 px-1 text-zinc-700 dark:bg-transparent dark:text-zinc-300").find("div", style="text-align: justify;").text
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "OLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def stefanellileiloes():
    soup = get_requests("https://wsww.stefanellileiloes.com.br/#")
    cards = soup.find_all("article", class_="col-md-3 col-sm-6")

    data = []
    for card in cards:
        name = card.find("header").find("h2", class_="bid-title").text.lstrip().rstrip()
        if "automovel" in name.lower() or "automóvel" in name.lower() or "carro" in name.lower() or "veiculo" in name.lower() or "veículo" in name.lower() or "moto" in name.lower() or "esmeraldas" in name.lower() or "joias" in name.lower() or "jóias" in name.lower() or "quilates" in name.lower():
            continue
        img_cover = card.find("header").find("img").get("src")
        link = card.find("footer", class_="clearfix").find("div", class_="bid-link").find("a").get("href")

        soup = get_requests(link)
        value1, value2 = None, None
        infos = soup.find_all("div", class_="info-line clearfix")[:7]
        for info in infos:
            info = info.text.replace("\n", "")
            if "avaliação" in info.lower():
                appraisal_value = float(info.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
            elif "1º leilão:r$"  in info.lower():
                value1 = float(info.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
            elif "2º leilão:r$"  in info.lower():
                value2 = float(info.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
            elif "localização"  in info.lower():
                address = info.split(":")[1].lstrip().rstrip()

        if value1 is not None and value2 is not None:
            value = min(value1, value2)
        elif value1 is not None and value2 is None:
            value = value1
        elif value1 is None and value2 is not None:
            value = value2
        else:
            value = None

        infos2 = soup.find_all("div", class_="col-sm-8")
        for info2 in infos2:
            try:
                info2 = info2.text
            except:  # noqa: E722
                continue
            if "Descrição detalhada do Lote" in info2:
                descricao = info2 
        
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "StefanelliLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def globoleiloes():
    cards = []
    soup = get_requests("https://www.globoleiloes.com.br/leiloes/todas-as-modalidades")
    cards_page = soup.find_all("div", class_="col-sm-3 item")
    for card in cards_page:
        cards.append(card)
    link_prox = soup.find("div", class_="col-sm-12 text-center").find_all("a")[4].get("href")
    link_prox = f"https://www.globoleiloes.com.br/leiloes/todas-as-modalidades{link_prox}"

    while True:
        try:
            soup = get_requests(link_prox)
            cards_page = soup.find_all("div", class_="col-sm-3 item")
            if cards_page not in cards:
                for card in cards_page:
                    cards.append(card)
                link_prox = soup.find("div", class_="col-sm-12 text-center").find_all("a")[-1].get("href")
                if "pagina" in link_prox:
                    link_prox = f"https://www.globoleiloes.com.br/leiloes/todas-as-modalidades{link_prox}"
                else:
                    break
            else:
                break
        except:  # noqa: E722
            break

    data = []
    for card in cards:
        link = card.find("div", class_="box no-padding").find("a").get("href")
        inf_img = card.find("div", class_="box no-padding").find("a").find("div", class_="bg-img").get("style").split("(")
        for inf in inf_img:
            if "http" in inf:
                img_cover = inf.split(")")[0].lstrip().rstrip()

        name = card.find_all("div", class_="box")[1].find("h3").text.replace("\n", "").lstrip().rstrip()
        if "onibus" in name.lower() or "ônibus" in name.lower() or "veiculo" in name.lower() or "veículo" in name.lower() or "carro" in name.lower() or "moto" in name.lower() or "vestido" in name.lower() or "vestidos" in name.lower() or "quotas" in name.lower() or "titularidade" in name.lower() or "caminhonete" in name.lower() or "computador" in name.lower() or "computadores" in name.lower():
            continue
        value = float(card.find_all("div", class_="box")[1].find("p").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        time.sleep(0.1)
        soup = get_requests(link)

        address = None
        appraisal_value = None
        area_total = None
        area_util = None

        try:
            address = soup.find("div", class_="bv-info-localizacao").find("i").text.replace("\n", ", ").replace(" , ", " ")
        except:  # noqa: E722
            try:
                address = soup.find("div", class_="col-md-12 p-0 py-4 bv-descricao-bem").find("p").find("div").find("div").text.lstrip().rstrip()
            except:  # noqa: E722
                pass
        try:
            descricao = soup.find("div", class_="col-md-12 p-0 py-4 bv-descricao-bem").find("div").text
            areas = get_areas(descricao)
            area_util = areas[0]
            area_total = areas[1]
        except:  # noqa: E722
            try: 
                descricao = soup.find("div", class_="public-DraftEditor-content").find("p").text
                areas = get_areas(descricao)

                area_util = areas[0]
                area_total = areas[1]

                infos = descricao.split("\n")
                for info in infos:
                    if "Valor da Avaliação:" in info:
                        appraisal_value = float(info.replace('.', '').replace(',', '.'))
            except:  # noqa: E722
                pass

        data_unit = {"Site": "GloboLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)   
    return data

def veronicaleiloes():
    urls = ["https://www.veronicaleiloes.com.br/leilao/lotes/imoveis"]
    cards = []
    for url in urls:
        soup = get_requests(url)
        cards_page = soup.find_all("div", class_="col-12 col-md-6 col-lg-4 col-xl-3")
        for card in cards_page:
            cards.append(card)

    data = []
    for card in cards:
        link = f"https://www.veronicaleiloes.com.br{card.find("div", class_="card-header card-header-image").find("a").get("href")}"
        img_cover = card.find("div", class_="card-header card-header-image").find("a").find("img").get("src")
        name = card.find("div", class_="card-body").find("h6").text.lstrip().rstrip()
        value = float(card.find("div", class_="card-body").find("p").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        address = None #Site só tem um item e não tem o campo
        area_util = None #Site só tem um item e não tem o campo
        area_total = None #Site só tem um item e não tem o campo
        appraisal_value = None #Site só tem um item e não tem o campo

        data_unit = {"Site": "VeronicaLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)   
    return data

def delltaleiloes():
    soup = get_selenium("https://www.delttaleiloes.com.br/home")
    cards = soup.find("div", class_="gtClassLote ng-star-inserted").find_all("div", class_="ng-star-inserted")
    data = []
    for card in cards:
        img_cover = card.find_all("div")[1].find("img", class_="mat-card-image ng-star-inserted").get("src")
        id_leilao = img_cover.split("/")
        link = f"https://www.delttaleiloes.com.br/pregao/{id_leilao[-3]}/{id_leilao[-2]}"
        name = card.find("div").find("h4").text
        if "automovel" in name.lower() or "automóvel" in name.lower() or "moto" in name.lower() or "carro" in name.lower() or "caminhonete" in name.lower() or "molduras" in name.lower():
            continue
        soup = get_selenium(link)

        values_list = []
        values = soup.find_all("div", style="margin-top: 15px; flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-between; align-items: stretch;")
        for x in values:
            x = x.text
            if "$" in x:
                values_list.append(float(x.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.')))
        value = min(values_list)

        descricao = soup.find("p", style="margin-top: 15px; text-align: justify; margin-bottom: 20px;").text
        if "rua" in descricao.lower():
            address = descricao
        else:
            address = None
        
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        appraisal_value = float(soup.find("div", style="flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-around; align-items: stretch;").find_all("div", style="flex-direction: column; box-sizing: border-box; display: flex;")[-1].find("b").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        data_unit = {"Site": "DelltaLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data
        
def krobelleiloes():
    soup = get_selenium("https://www.krobelleiloes.com.br/home")
    cards = soup.find("div", class_="gtClassLote ng-star-inserted").find_all("div", class_="ng-star-inserted")
    data = []
    for card in cards:
        img_cover = card.find_all("div")[1].find("img", class_="mat-card-image ng-star-inserted").get("src")
        id_leilao = img_cover.split("/")
        link = f"https://www.krobelleiloes.com.br/pregao/{id_leilao[-3]}/{id_leilao[-2]}"
        name = card.find("div").find("h4").text
        if "fiesta" in name.lower() or "carro" in name.lower() or "moto" in name.lower() or "veiculo" in name.lower() or "veículo" in name.lower() or "honda" in name.lower():
        soup = get_selenium(link)

        values_list = []
        values = soup.find_all("div", style="margin-top: 15px; flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-between; align-items: stretch;")
        for x in values:
            x = x.text
            if "$" in x:
                values_list.append(float(x.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.')))
        value = min(values_list)

        descricao = soup.find("p", style="margin-top: 15px; text-align: justify; margin-bottom: 20px;").text.replace("\n\xa0\n", " ")
        if "rua" in descricao.lower():
            address = descricao
        else:
            address = None
        
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        try:
            appraisal_value = float(soup.find("div", style="flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-around; align-items: stretch;").find_all("div", style="flex-direction: column; box-sizing: border-box; display: flex;")[-1].find("b").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            appraisal_value = float(soup.find_all("div", style="flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-around; align-items: stretch;")[1].find_all("div")[-1].find("b").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        data_unit = {"Site": "KrobelLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def mazzollileiloes():
    soup = get_selenium("https://mazzollileiloes.com.br/home")
    cards = soup.find("div", class_="gtClassLote ng-star-inserted").find_all("div", class_="ng-star-inserted")
    data = []
    for card in cards:
        img_cover = card.find_all("div")[1].find("img", class_="mat-card-image ng-star-inserted").get("src")
        id_leilao = img_cover.split("/")
        link = f"https://mazzollileiloes.com.br/pregao/{id_leilao[-3]}/{id_leilao[-2]}"
        name = card.find("div").find("h4").text

        soup = get_selenium(link)

        values_list = []
        values = soup.find_all("div", style="margin-top: 15px; flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-between; align-items: stretch;")
        for x in values:
            x = x.text
            if "$" in x:
                values_list.append(float(x.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.')))
        value = min(values_list)

        descricao = soup.find("p", style="margin-top: 15px; text-align: justify; margin-bottom: 20px;").text.replace("\n\xa0\n", " ")
        if "rua" in descricao.lower():
            address = descricao
        else:
            address = None
        
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        try:
            appraisal_value = float(soup.find("div", style="flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-around; align-items: stretch;").find_all("div", style="flex-direction: column; box-sizing: border-box; display: flex;")[-1].find("b").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            appraisal_value = float(soup.find_all("div", style="flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-around; align-items: stretch;")[1].find_all("div")[-1].find("b").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        data_unit = {"Site": "MazzolliLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def oesteleiloes():
    soup = get_selenium("https://www.oesteleiloes.com.br/home")
    cards = soup.find("div", class_="gtClassLote ng-star-inserted").find_all("div", class_="ng-star-inserted")
    data = []
    for card in cards:
        img_cover = card.find_all("div")[1].find("img", class_="mat-card-image ng-star-inserted").get("src")
        id_leilao = img_cover.split("/")
        link = f"https://www.oesteleiloes.com.br/pregao/{id_leilao[-3]}/{id_leilao[-2]}"
        name = card.find("div").find("h4").text

        soup = get_selenium(link)

        values_list = []
        values = soup.find_all("div", style="margin-top: 15px; flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-between; align-items: stretch;")
        for x in values:
            x = x.text
            if "$" in x:
                values_list.append(float(x.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.')))
        value = min(values_list)

        descricao = soup.find("p", style="margin-top: 15px; text-align: justify; margin-bottom: 20px;").text.replace("\n\xa0\n", " ")
        if "rua" in descricao.lower():
            address = descricao
        else:
            address = None
        
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        try:
            appraisal_value = float(soup.find("div", style="flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-around; align-items: stretch;").find_all("div", style="flex-direction: column; box-sizing: border-box; display: flex;")[-1].find("b").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            appraisal_value = float(soup.find_all("div", style="flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-around; align-items: stretch;")[1].find_all("div")[-1].find("b").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        data_unit = {"Site": "OesteLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def nordesteleiloes():
    soup = get_selenium("https://www.nordesteleiloes.com.br/?searchType=opened&preOrderBy=orderByFirstOpenedOffers&pageNumber=1&pageSize=9999999&orderBy=endDate:asc")
    cards = soup.find_all("div", class_="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-md-12 css-1ojex0")

    data = []
    for card in cards:
        link = card.find("div", class_="react-swipeable-view-container").find("a").get("href")
        link = f"https://www.nordesteleiloes.com.br{link}"
        img_cover = card.find("div", class_="react-swipeable-view-container").find("a").find("img").get("src")
        name = card.get("data-auction-category").lstrip().rstrip()
        value = float(card.find("p", class_="MuiTypography-root MuiTypography-body1 jss363 css-z355qp").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        address = card.find("p", class_="MuiTypography-root MuiTypography-body1 jss370 css-z355qp").text.lstrip().rstrip()
        
        soup = get_selenium(link)
        descricao = soup.find("div", class_="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-md-12 MuiGrid-grid-lg-12 css-1ojex0").text

        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        appraisal_value = None
        try:
            if "Avaliação:" in descricao:
                infos = descricao.split("Avaliação:")
                for info in infos:
                    appraisal_value = float(info.split("$")[1].split()[0].lstrip().rstrip().replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            pass
        data_unit = {"Site": "NordesteLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def portellaleiloes():
    soup = get_requests("https://www.portellaleiloes.com.br/#proximos-tab")
    cards = soup.find_all("article", class_="col-md-4 col-sm-6")

    data = []
    for card in cards:
        link = card.find("header").find("a").get("href")
        img_cover = card.find("header").find("a").find("img").get("src")
        name = card.find("header").find("h2", class_="bid-title").text.lstrip().rstrip()
        address = card.find("div", class_="bid-details").find("p", class_="bid-description").text.lstrip().rstrip()
        if "rua" not in address.lower() and "terreno" not in address.lower() and "avenida" not in address.lower():
            address = None
        infos = card.find("div", class_="bid-infos").find_all("p", class_="right")
        values = []
        for info in infos:
            info = info.text
            if "$" in info:
                values.append(float(info.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.')))
        value = min(values)

        soup = get_requests(link)
        infos2 = soup.find_all("div", class_="info-line clearfix")
        for info in infos2:
            info = info.text
            if "Avaliação:" in info:
                appraisal_value = float(info.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        
        descricao = soup.find("div", style="font-size: 18px !important;")
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "PortellaLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def rochaleiloes():
    cards = []
    x=0
    while True:
        try:
            x+=1
            soup = get_requests(f"https://rochaleiloes.com.br/?page={x}")
            verify = soup.find("div", class_="h-52 relative overflow-hidden rounded-t-md").text  # noqa: F841
            cards_page = soup.find_all("div", class_="hover:shadow-2xl transition-all ease-in shadow-zinc-100 shadow-sm dark:shadow-zinc-800 dark:bg-gradient-to-t dark:from-zinc-800 dark:to-zinc-800 border-[1px] bg-white dark:border-zinc-800 mb-2 rounded-md md:m-0 m-2 group")
            for card in cards_page:
                cards.append(card)
        except:  # noqa: E722
            break
    
    data = []
    for card in cards:
        link = card.find("div", class_="relative").find("a").get("href")
        img_cover = card.find("div", class_="relative").find("a").find("img").get("src")
        address = card.find("div", class_="px-4 uppercase text-center font-bold text-site-box-cidade dark:text-site-box-cidade-dark py-2 text-[1.25rem]").find("span").text.lstrip().rstrip()
        name = card.find("a", class_="font-bold text-site-box-titulo dark:text-site-box-titulo-dark")

        values = []
        values_inf = card.find("div", class_="flex-1 text-center").find_all("span")
        for value_x in values_inf:
            value_x = value_x.text.replace("\n", " ")
            if "$" in value_x:
                try:
                    value_x = float(value_x.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
                    values.append(value_x)
                except:  # noqa: E722
                    pass
        try:
            value = min(values)
        except:  # noqa: E722
            value = None

        soup = get_requests(link)
        infos = soup.find_all("tr", class_="odd:bg-white even:bg-zinc-50 dark:text-zinc-300 dark:odd:bg-zinc-700 dark:even:bg-zinc-800")
        for info in infos:
            info = info.text
            if "Valor da avaliação:" in info:
                appraisal_value = float(info.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        area_util = None
        area_total = None
        try:
            descricao = soup.find("div", class_="py-2 px-1 text-zinc-700 dark:bg-transparent dark:text-zinc-300").text
            areas = get_areas(descricao)
            area_util = areas[0]
            area_total = areas[1]
        except:  # noqa: E722
            pass

        data_unit = {"Site": "RochaLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def centraljudicial():
    soup = get_requests("https://www.centraljudicial.com.br/pesquisa.php?classificacao=&uf=&cidade=&bairro=")
    cards = soup.find_all("div", class_="mb-4 lotePadrao rounded lote-borda")

    data = []
    for card in cards:
        link = f"https://www.centraljudicial.com.br/{card.find("div", class_="col-lg-8 col-sm-12 px-lg-1").get("onclick").split("'")[1]}"
        img_cover = f"https://www.centraljudicial.com.br/{card.find("div", class_="col-12 m-0 pb-1").find("img").get("src")}"
        descricao = card.find_all("div", class_="lote-descricao")[-1].find("p").text
        name = f"{descricao[:50]}..."#Site não tem nome do imóvel, então peguei os 50 primeiros caracteres da descrição
        
        infos = card.find("div", class_="pt-1 h-100").find("div", class_="row").find_all("div")
        for info in infos:
            info = info.text
            if "Avaliação" in info:
                appraisal_value = float(info.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
            if "Inicial" in info:
                value = float(info.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        soup = get_requests(link)
        address = soup.find("div", class_="text-justify mt-2 small").find("a").text.lstrip().rstrip()

        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]
        
        data_unit = {"Site": "CentralJudicial",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def simonleiloes():
    urls = ["https://www.simonleiloes.com.br/categoria/imoveis-urbanos", "https://www.simonleiloes.com.br/categoria/imoveis-rurais", "https://www.simonleiloes.com.br/categoria/automoveis", "https://www.simonleiloes.com.br/categoria/Onibus", "https://www.simonleiloes.com.br/categoria/motos", "https://www.simonleiloes.com.br/categoria/sucatas", "https://www.simonleiloes.com.br/categoria/aerogerador", "https://www.simonleiloes.com.br/categoria/outros"]
    cards = []
    for url in urls:
        soup = get_requests(url)
        cards_page = soup.find("div", id="lista-bens").find_all("div", class_="cx-bemleilao row")
        for card in cards_page:
            cards.append(card)

    data = []
    for card in cards:
        img_cover = f"https://www.simonleiloes.com.br{card.find("div", class_="col-md-3 infolote").find("a", class_="imglote").find("img", class_="imglote").get("src")}"
        link = f"https://www.simonleiloes.com.br{card.find("div", class_="col-md-3 infolote").find("a", class_="imglote").get("href")}"
        descricao = card.find("div", class_="textoDescricaoLote").find("p").text
        name = f"{descricao[:50]}..." #site não tem nome, então usei os 50 primeiros caracteres da descrição
        values = card.find("div", class_="valorlote").find_all("p")
        for x in values:
            x = x.text
            if "Valor de Avaliação:" in x:
                appraisal_value = float(x.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
            elif "$" in x:
                value = float(x.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        
        address = None #não tem o campo no site

        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "SimonLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def nogarileiloes():
    urls = ["https://www.nogarileiloes.com.br/lotes/imovel", "https://www.nogarileiloes.com.br/lotes/diversos", "https://www.nogarileiloes.com.br/lotes/veiculo"]
    cards = []
    for url in urls:
        soup = get_requests(url)
        cards_page = soup.find("div", class_="lista-lotes").find_all("div", class_="lote")
        for card in cards_page:
            cards.append(card)

    data = []
    for card in cards:
        link = card.find("div", class_="col-12 col-lg-2").find("a", class_="rounded").get("href")
        styles = card.find("div", class_="col-12 col-lg-2").find("a", class_="rounded").get("style").split("'")
        for s in styles:
            if "http" in s:
                img_cover = s.lstrip().rstrip()
        name = card.find("div", class_="col-12 col-lg-7 text-justify").find("h5").text
        address = None
        try:
            address = card.find("div", class_="col-12 col-lg-7 text-justify").find("div").text.replace("\n", " ").split("Matrícula:")[0].lstrip().rstrip()

            while "  " in address:
                address = address.replace("  ", " ")
        except:  # noqa: E722
            None
        if "rua" in address[:100].lower() or "travessa" in address[:100].lower() or "avenida" in address[:100].lower() or "estrada" in address[:100].lower():
            pass
        else:
            address = None
        
        soup = get_requests(link)
        values=[]
        value = None
        try:
            values_x = soup.find("div", class_="col-12 col-lg-4 float-right p-1").find_all("h6")
            for x in values_x:
                x = x.text
                if "Valor de Avaliação:" in x:
                    appraisal_value = float(x.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
                elif "Lance Inicial:" in x:
                    values.append(float(x.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.')))
            value = min(values)
        except:  # noqa: E722
            pass
        
        descricao = soup.find("div", class_="mb-3 p-2 border rounded text-justify").text

        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "NogariLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def trileiloes():
    x = 1
    cards = []
    while True:
        try:
            soup = get_requests(f"https://www.trileiloes.com.br/busca?page={x}")
            verify = soup.find("div", class_="flex-leiloes").find("div", class_="item").find("span", class_="tag isOferta").text  # noqa: F841
            cards_page = soup.find("div", class_="flex-leiloes").find_all("div", class_="item")
            for card in cards_page:
                cards.append(card)
            x+=1
        except:  # noqa: E722
            break
    
    data = []
    for card in cards: 
        link = f"https://www.trileiloes.com.br{card.find("div", class_="fotos-lotes").find("div", class_="item-img").find("a").get("href")}"
        img_cover = card.find("div", class_="fotos-lotes").find("div", class_="item-img").find("a").find("img").get("src")
        address = card.find("span", style="left: -3px; width: 100%; white-space: nowrap;").text.replace("\n", " ").lstrip().rstrip()
        while "  " in address:
            address = address.replace("  ", " ")
        
        soup = get_requests(link)
        name = soup.find("div", class_="g-right").find("div", class_="r3").text.lstrip().rstrip().replace("\n", " ")
        while "  " in name:
            name = name.replace("  ", " ")
        
        values_pts = soup.find("div", class_="g-right").find("div", class_="r2").text.split("\n\n")
        for value_pt in values_pts:
            if "Valor de venda" in value_pt:
                value = float(value_pt.replace("\n", " ").split("$")[1].split()[0].lstrip().rstrip().replace('.', '').replace(',', '.'))
            elif "Valor avaliado" in value_pt:
                appraisal_value = float(value_pt.replace("\n", " ").split("$")[1].split()[0].lstrip().rstrip().replace('.', '').replace(',', '.'))

        descricao = soup.find("main", class_="main-lote").find("div", class_="p").text
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "TriLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def alfaleiloes():
    cards = []
    x=1
    while True:
        try:
            soup = get_selenium(f"https://www.alfaleiloes.com/leiloes/?page={x}")
            cards_page = soup.find_all("div", class_="home-leiloes-cards")
            verify = cards_page[1].find("div", class_="card-content").text.lstrip().rstrip()  # noqa: F841
            for card in cards_page:
                cards.append(card)
        except:  # noqa: E722
            break

    data = []
    for card in cards:
        link = f"https://www.alfaleiloes.com{card.find("div", class_="card-image").find("a").get("href")}"
        img_cover = card.find("div", class_="card-image").find("a").find("img").get("src")
        name = card.find("div", class_="card-content").text.lstrip().rstrip()

        values = []
        value = None
        values_divs = card.find_all("div", class_="card-lances")
        for value_div in values_divs:
            value_div = value_div.text
            if "R$" in value_div:
                values.append(float(value_div.split("$")[1].split()[0].lstrip().rstrip().replace('.', '').replace(',', '.')))
        try:
            value = min(values)
        except:  # noqa: E722
            pass
        soup = get_selenium(link)
        
        address = None
        appraisal_value = None
        try:
            infos = soup.find("div", class_="lote-col-2").find("div", class_="content").text.split("\n")

            for info in infos:
                if "situado na" in info.lower():
                    address = info.split("situado na")[1].split(".")[0].lstrip().rstrip()
                elif "situado no" in info.lower():
                    address = info.split("situado no")[1].split(".")[0].lstrip().rstrip()
                elif "situadas na" in info.lower():
                    address = info.split("situadas na")[1].split(".")[0].lstrip().rstrip()
                elif "situados no" in info.lower():
                    address = info.split("situados no")[1].split(".")[0].lstrip().rstrip()
                elif "Valor da Avaliação" in info:
                    appraisal_value = float(info.split("$")[1].split("L")[0].lstrip().rstrip().replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            pass
        area_util = None
        try:
            area_util = float(soup.find("div", title="Metragem").text.lstrip().rstrip().split()[0])
        except:  # noqa: E722
            pass
        area_total = None #sem campo no site

        data_unit = {"Site": "TriLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)       
    return data

def wspleiloes():

    soup = get_selenium("https://www.wspleiloes.com.br/")
    
    cards = soup.find_all("div", class_="col-md-6 col-lg-4 col-xl-3 p-2")

    data = []
    for card in cards:
        img_cover = card.find("img", class_="my-auto").get("src")
        name = card.find("h6", class_="card-title m-0").text
        link = card.find("div", class_="card-body d-flex flex-column").find("a").get("href")
        link_card = card.find("div").find("div").find("a").get("href")
        link_details = get_requests(link_card).find("a", class_="btn btn-block btn-dark").get("href")
        infos = get_requests(link_details)

        try:
            address = infos.find("div", class_="mb-3 p-2 border rounded text-justify").find("div").text.split('\n')
            for linha in address:
                if "Cidade:" in linha:
                    city1 = linha.split("Cidade:")

                    if len(city1) > 1:
                        city = city1[1].strip()
                        
                if "Endereço:" in linha:
                    address_p = linha.split("Endereço:")

                    if len(address_p) > 1:
                        address1 = address_p[1].strip()
                        break
            address = f"{address1}, {city}"

        except:  # noqa: E722
            address = ""

        infos2 = infos.find_all("div", class_="my-2 p-2 border rounded text-center")[2]
        try:
            initial_bids = infos2.find_all(string=re.compile("Lance Inicial:"))

            values = [re.search(r'R\$(\d+.\d+,\d+)', bid).group(1) for bid in initial_bids]
            value1, value2 = float(values[0].replace("R$", "")), float(values[1].replace("R$", ""))
            value = min(value1.replace('.', '').replace(',', '.'), value2.replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            infos3 = infos2.find_all("h6", class_="text-center border-top p-2 m-0")
            for info in infos3:
                linhas = info.text.split('\n')
                for linha in linhas:
                    if "Lance Inicial:" in linha:
                        value1 = linha.split("Lance Inicial:")

                        if len(value1) > 1:
                            value = float(value1[1].strip().replace("R$", "").replace('.', '').replace(',', '.'))
        
        appraisal_value = None
        try:
            for info in infos2:
                linhas = info.get_text().split('\n')
                for linha in linhas:
                    if "Valor de Avaliação:" in linha:
                        value1 = linha.split("Valor de Avaliação:")
                        if len(value1) > 1:
                            appraisal_value = float(value1[1].strip().replace("R$", "").replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            appraisal_value = 0

        area_util = None
        area_total = None
        
        try:
            descricao_div = infos.find("div", class_="col-12 col-lg-8 p-1 float-left")
            
            if descricao_div:
                descricao_texto = descricao_div.get_text()  # Captura todo o texto dentro do div

                # Tentar encontrar a área privativa/útil
                area_util_match = re.search(r'área (privativa|útil) de ([\d,\.]+)m2', descricao_texto)
                area_util = area_util_match.group(2) if area_util_match else None

                # Tentar encontrar a área total
                area_total_match = re.search(r'total de ([\d,\.]+)m2', descricao_texto)
                area_total = area_total_match.group(1) if area_total_match else None
            else:
                result = chat_gpt(descricao_texto)
                try:
                    result = result.split('\n')
                except:  # noqa: E722
                    try:
                        result = result.split(' ')
                    except:  # noqa: E722
                        pass

                try:
                    area_util = result[0]
                except:  # noqa: E722
                    area_util = None
                
                try:
                    area_total = result[1]
                except:  # noqa: E722
                    area_total = None

        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            area_util = None
            area_total = None

        data_unit = {"Site": "WspLeiloes",
                     "Nome": name,
                     "Endereço": address,
                     "Área Útil": area_util,
                     "Área Total": area_total,
                     "Valor": value,
                     "Valor da Avaliação": appraisal_value,
                     "Link oferta": link,
                     "Link imagem da capa": img_cover
                     }
        data.append(data_unit)
    return data

def fidalgoleiloes():
    x=1
    cards = []
    while True:
        try:
            soup = get_requests(f"https://www.fidalgoleiloes.com.br/pesquisa.php?nothing=&pagina={x}")
            cards_page = soup.find_all("div", class_="col-md-6 col-lg-4 mb-4")
            verify = cards_page[0].find("div", class_="loteCartaBens").find("div", class_="mb-2").text.replace("Local:", "").lstrip().rstrip()  # noqa: F841
            for card in cards_page:
                cards.append(card)
            x+=1
        except:  # noqa: E722
            break
    
    data = []
    for card in cards:
        address = card.find("div", class_="loteCartaBens").find("div", class_="mb-2").text.replace("Local:", "").lstrip().rstrip()
        link = f"https://www.fidalgoleiloes.com.br/{card.find("div", class_="d-block lote-imagem").find("a").get("href")}"
        img_cover = f"https://www.fidalgoleiloes.com.br/{card.find("div", class_="d-block lote-imagem").find("a").find("img").get("href")}"
        name = card.find("div", class_="loteCartaBens").find("div", style="min-height: 60px").text.lstrip().rstrip()
        value = float(card.find("div", class_="loteCartaBens").find("div", class_="loteCartaInicial pt-1").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        soup = get_requests(link)

        descricao = soup.find("div", class_="text-justify lote-detalhe-descricao").text

        appraisal_value = None
        try:
            infos = descricao.split("\n")
            for info in infos:
                if "Avaliação:" in info:
                    appraisal_value = float(info.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            pass

        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "FidalgoLeiloes",
                     "Nome": name,
                     "Endereço": address,
                     "Área Útil": area_util,
                     "Área Total": area_total,
                     "Valor": value,
                     "Valor da Avaliação": appraisal_value,
                     "Link oferta": link,
                     "Link imagem da capa": img_cover
                     }
        data.append(data_unit)
    return data

def damianileiloes():
    soup = get_selenium_more_visited("https://www.damianileiloes.com.br/home")
    cards = soup.find("div", class_="gtClassLote ng-star-inserted").find_all("div", class_="ng-star-inserted")
    data = []
    for card in cards:
        img_cover = card.find_all("div")[1].find("img", class_="mat-card-image ng-star-inserted").get("src")
        id_leilao = img_cover.split("/")
        link = f"https://www.damianileiloes.com.br/pregao/{id_leilao[-3]}/{id_leilao[-2]}"
        name = card.find("div").find("h4").text

        soup = get_selenium(link)

        values_list = []
        value = None
        values = soup.find_all("div", style="margin-top: 15px; flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-between; align-items: stretch;")
        for x in values:
            x = x.text
            if "$" in x:
                values_list.append(float(x.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.')))
        try:
            value = min(values_list)
        except:  # noqa: E722
            pass

        descricao = soup.find("p", style="margin-top: 15px; text-align: justify; margin-bottom: 20px;").text.replace("\n\xa0\n", " ")
        
        infos = soup.find("mat-card", class_="mat-card mat-focus-indicator ng-star-inserted").find_all("p")
        infos_add = []
        for info in infos:
            info = info.text
            if "Endereço:" in info:
                infos_add.append(info.split("Endereço:")[1].lstrip().rstrip())
            elif "Cidade/Estado:" in info:   
                infos_add.append(info.split("Cidade/Estado:")[1].lstrip().rstrip())
        address = f"{infos_add[1]}, {infos_add[0]}"
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        try:
            appraisal_value = float(soup.find("div", style="flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-around; align-items: stretch;").find_all("div", style="flex-direction: column; box-sizing: border-box; display: flex;")[-1].find("b").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            appraisal_value = float(soup.find_all("div", style="flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-around; align-items: stretch;")[1].find_all("div")[-1].find("b").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        data_unit = {"Site": "DamianiLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def joaoemilio():
    urls = ["https://joaoemilio.com.br/lotes/imovel?tipo=imovel&page=", "https://joaoemilio.com.br/lotes/veiculo?tipo=veiculo&page=", "https://joaoemilio.com.br/lotes/diversos?tipo=diversos&page="]
    data = []
    cards = []
    for url in urls:
        soup = get_requests(url)
        links = []
        try:
            bar = soup.find("ul", class_="pagination justify-content-center")
            lis = bar.find_all("li", class_="page-item")
            numero_paginas = int(lis[-2].text)

            for x in range(numero_paginas):
                links.append(f"{url}{x+1}")

            for link in links:
                page = get_requests(link)
                cards_page = page.find_all("div", class_="lote")
                for card in cards_page:
                    cards.append(card)

        except:  # noqa: E722
            cards_page = soup.find_all("div", class_="lote")
            for card in cards_page:
                cards.append(card)

    for card in cards:
        img = card.find("div", class_="col-12 col-lg-2").find("a", class_="rounded").get("style")
        img = re.search(r"url\('([^']+)'\)", img)
        img_cover = img.group(1) if img else None

        name = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").find("h5").text
        
        info_div = card.find("div", class_="col-12 col-lg-7 text-justify")

        try:
            address = info_div.find("div").find("div").text.split('\n')
            for linha in address:
                if "Cidade:" in linha:
                    city1 = linha.split("Cidade:")

                    if len(city1) > 1:
                        city = city1[1].strip()
                        
                if "Endereço:" in linha:
                    address_p = linha.split("Endereço:")

                    if len(address_p) > 1:
                        address1 = address_p[1].strip().split('   ')[0]
                        break
            address = f"{address1}, {city}"
            
        except:  # noqa: E722
            address = None

        link = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").get("href")      
        soup = get_requests(link)
        
        def extrair_valor(texto):
            if texto:
                match = re.search(r'R\$([\d\.]+,\d+)', texto)
                return match.group(1) if match else None
            return None

        # Encontrar todos os elementos <h6>
        h6_elements = soup.find_all('h6', class_="text-center border-top p-2 m-0")

        # Inicializando variáveis
        appraisal_value = None
        value1 = None
        value2 = None

        # Iterar sobre os elementos encontrados
        for element in h6_elements:
            if "Valor de Avaliação:" in element.text:
                appraisal_value = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
            elif "Lance Inicial:" in element.text:
                if value1 is None:
                    value1 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
                else:
                    value2 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))

        if value1 and value2 is not None:
            value = min(value1, value2)
        
        elif value1 is not None:
            value = value1

        elif value2 is not None:
            value = value2

        else:
            value = None

        descricao = soup.find("div", class_="mb-3 p-2 border rounded text-justify").find_all("div")[1].text
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "JoaoEmilio",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link,
                        "Link imagem da capa": img_cover
                        }
        data.append(data_unit)
    return data

def cravoleiloes():
    urls = ["https://www.cravoleiloes.com.br/lotes/imovel?tipo=imovel&page=", "https://www.cravoleiloes.com.br/lotes/veiculo?tipo=veiculo&page=", "https://www.cravoleiloes.com.br/lotes/diversos?tipo=diversos&page="]
    data = []
    cards = []
    for url in urls:
        soup = get_requests(url)
        links = []
        try:
            bar = soup.find("ul", class_="pagination justify-content-center")
            lis = bar.find_all("li", class_="page-item")
            numero_paginas = int(lis[-2].text)

            for x in range(numero_paginas):
                links.append(f"{url}{x+1}")

            for link in links:
                page = get_requests(link)
                cards_page = page.find_all("div", class_="lote")
                for card in cards_page:
                    cards.append(card)

        except:  # noqa: E722
            cards_page = soup.find_all("div", class_="lote")
            for card in cards_page:
                cards.append(card)

    for card in cards:
        img = card.find("div", class_="col-12 col-lg-2").find("a", class_="rounded").get("style")
        img = re.search(r"url\('([^']+)'\)", img)
        img_cover = img.group(1) if img else None

        name = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").find("h5").text
        
        info_div = card.find("div", class_="col-12 col-lg-7 text-justify")

        try:
            address = info_div.find("div").find("div").text.split('\n')
            for linha in address:
                if "Cidade:" in linha:
                    city1 = linha.split("Cidade:")

                    if len(city1) > 1:
                        city = city1[1].strip()
                        
                if "Endereço:" in linha:
                    address_p = linha.split("Endereço:")

                    if len(address_p) > 1:
                        address1 = address_p[1].strip().split('   ')[0]
                        break
            address = f"{address1}, {city}"
            
        except:  # noqa: E722
            address = None

        link = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").get("href")      
        if "https://www.cravoleiloes" not in link:
            continue
        soup = get_requests(link)
        
        def extrair_valor(texto):
            if texto:
                match = re.search(r'R\$([\d\.]+,\d+)', texto)
                return match.group(1) if match else None
            return None

        # Encontrar todos os elementos <h6>
        h6_elements = soup.find_all('h6', class_="text-center border-top p-2 m-0")

        # Inicializando variáveis
        appraisal_value = None
        value1 = None
        value2 = None

        # Iterar sobre os elementos encontrados
        for element in h6_elements:
            if "Valor de Avaliação:" in element.text:
                appraisal_value = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
            elif "Lance Inicial:" in element.text:
                if value1 is None:
                    value1 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
                else:
                    value2 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))

        if value1 and value2 is not None:
            value = min(value1, value2)
        
        elif value1 is not None:
            value = value1

        elif value2 is not None:
            value = value2

        else:
            value = None

        descricao = soup.find("div", class_="mb-3 p-2 border rounded text-justify").find_all("div")[1].text
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "CravoLeiloes",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link,
                        "Link imagem da capa": img_cover
                        }
        data.append(data_unit)
    return data

def topleiloes():
    soup = get_selenium_more_visited("https://www.topleiloes.com.br/home")
    cards = soup.find("div", class_="gtClassLote ng-star-inserted").find_all("div", class_="ng-star-inserted")
    data = []
    for card in cards:
        img_cover = card.find_all("div")[1].find("img", class_="mat-card-image ng-star-inserted").get("src")
        id_leilao = img_cover.split("/")
        link = f"https://www.topleiloes.com.br/pregao/{id_leilao[-3]}/{id_leilao[-2]}"
        name = card.find("div").find("h4").text

        soup = get_selenium(link)

        values_list = []
        value = None
        values = soup.find_all("div", style="margin-top: 15px; flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-between; align-items: stretch;")
        for x in values:
            x = x.text
            if "$" in x:
                values_list.append(float(x.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.')))
        try:
            value = min(values_list)
        except:  # noqa: E722
            pass

        descricao = soup.find("p", style="margin-top: 15px; text-align: justify; margin-bottom: 20px;").text.replace("\n\xa0\n", " ")
        
        infos = soup.find("mat-card", class_="mat-card mat-focus-indicator ng-star-inserted").find_all("p")
        infos_add = []
        for info in infos:
            info = info.text
            if "Endereço:" in info:
                infos_add.append(info.split("Endereço:")[1].lstrip().rstrip())
            elif "Cidade/Estado:" in info:   
                infos_add.append(info.split("Cidade/Estado:")[1].lstrip().rstrip())
        address = f"{infos_add[1]}, {infos_add[0]}"
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        appraisal_value = None
        try:
            appraisal_value = float(soup.find("div", style="flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-around; align-items: stretch;").find_all("div", style="flex-direction: column; box-sizing: border-box; display: flex;")[-1].find("b").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            try:
                appraisal_value = float(soup.find_all("div", style="flex-direction: row; box-sizing: border-box; display: flex; place-content: stretch space-around; align-items: stretch;")[1].find_all("div")[-1].find("b").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
            except:  # noqa: E722
                pass

        data_unit = {"Site": "TopLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def valerioiaminleiloes():
    soup = get_requests("https://www.valerioiaminleiloes.com.br/leilao/proximos")
    cards_lotes = soup.find_all("div", class_="col-12 col-sm-4 col-xl-3")
    
    cards = []
    for card_lote in cards_lotes:
        soup = get_requests(card_lote.find("div", class_="back").find("a").get("href"))
        cards_page = soup.find_all("div", class_="card card-lote-interno")
        for card in cards_page:
            cards.append(card)
    
    data = []
    for card in cards:
        name = card.find("h4", class_="card-title").text.split("-")[1].lstrip().rstrip()
        link = f"https://www.valerioiaminleiloes.com.br{card.find("div", class_="col-12 col-lg-4").find("a").get("href")}"
        if "http" in card.find("div", class_="col-12 col-lg-4").find("a").find("img").get("src"):
            img_cover = card.find("div", class_="col-12 col-lg-4").find("a").find("img").get("src")
        else:
            img_cover = f"https://www.valerioiaminleiloes.com.br{card.find("div", class_="col-12 col-lg-4").find("a").find("img").get("src")}"
        
        soup = get_requests(link)

        value = float(soup.find("div", class_="row cards-valores").find("div", class_="card-body").find("p").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        appraisal_value = float(soup.find("div", class_="col-12 col-lg-7").find("div", class_="col-12 col-sm-4").find("h4").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        descricao = soup.find("div", class_="col-12 descricao").text
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        address = None #não tem campo no site
        data_unit = {"Site": "ValerioIaminLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def renovarleiloes():
    cards = []
    
    urls = ["https://www.renovarleiloes.com.br/leilao/lotes/imoveis", "https://www.renovarleiloes.com.br/leilao/lotes/diversos", "https://www.renovarleiloes.com.br/leilao/lotes/eletronicos", "https://www.renovarleiloes.com.br/leilao/lotes/embarcacao", "https://www.renovarleiloes.com.br/leilao/lotes/equipamentos", "https://www.renovarleiloes.com.br/leilao/lotes/maquinas", "https://www.renovarleiloes.com.br/leilao/lotes/semoventes", "https://www.renovarleiloes.com.br/leilao/lotes/sucatas", "https://www.renovarleiloes.com.br/leilao/lotes/veiculos"]
    for url in urls:
        x = 1
        while True:
            try:
                soup = get_requests(f"{url}?page_a={x}")
                cards_page = soup.find_all("div", class_="col-12 col-md-6 col-lg-4 col-xl-3")
                if len(cards_page) > 0:
                    for card in cards_page:
                        cards.append(card)
                    x += 1
                else:
                    break
            except:  # noqa: E722
                break
    
    data = []
    for card in cards:
        link = f"https://www.renovarleiloes.com.br{card.find("div", class_="back").find("div", class_="card-footer").find("a").get("href")}"
        img_cover = card.find("div", class_="front").find("div", class_="carousel-inner").find("img").get("src")
        
        soup = get_requests(link)
        name = soup.find("h4", class_="card-title").text.replace("\n", "").lstrip().rstrip()
        value = float(soup.find("p", class_="lance-inicial-valor").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        appraisal_value = float(soup.find("div", class_="card-body text-center").find("h4").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        descricao = soup.find("div", class_="col-12 descricao").text
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        address = None #não tem campo no site
        data_unit = {"Site": "RenovarLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def agenciadeleiloes():
    cards = []
    
    urls = ["https://www.agenciadeleiloes.com.br/leilao/lotes/imoveis", "https://www.agenciadeleiloes.com.br/leilao/lotes/arte", "https://www.agenciadeleiloes.com.br/leilao/lotes/arte-1", "https://www.agenciadeleiloes.com.br/leilao/lotes/diversos", "https://www.agenciadeleiloes.com.br/leilao/lotes/eletronicos", "https://www.agenciadeleiloes.com.br/leilao/lotes/equipamentos", "https://www.agenciadeleiloes.com.br/leilao/lotes/escultura", "https://www.agenciadeleiloes.com.br/leilao/lotes/escultura-1", "https://www.agenciadeleiloes.com.br/leilao/lotes/maquinas", "https://www.agenciadeleiloes.com.br/leilao/lotes/moveis", "https://www.agenciadeleiloes.com.br/leilao/lotes/sucatas", "https://www.agenciadeleiloes.com.br/leilao/lotes/veiculos"]
    for url in urls:
        try:
            soup = get_requests(url)
            cards_page = soup.find_all("div", class_="col-12 col-md-6 col-lg-4 col-xl-3")
            for card in cards_page:
                cards.append(card)
        except:  # noqa: E722
            break

    data = []
    for card in cards:
        try:
            link = f"https://www.agenciadeleiloes.com.br{card.find("div", class_="back").find("div", class_="card-footer").find("a").get("href")}"
            img_cover = card.find("div", class_="front").find("div", class_="carousel-inner").find("img").get("src")
        except:  # noqa: E722
            link = f"https://www.agenciadeleiloes.com.br{card.find("div", class_="card-header card-header-image").find("a").get("href")}"
            img_cover = card.find("div", class_="card-header card-header-image").find("img").get("src")
        soup = get_requests(link)
        name = soup.find("h4", class_="card-title").text.replace("\n", "").lstrip().rstrip()
        value = float(soup.find("p", class_="lance-inicial-valor").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        appraisal_value = None
        try:
            appraisal_value = float(soup.find("div", class_="card-body text-center").find("h4").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            pass
        descricao = soup.find("div", class_="col-12 descricao").text
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        address = None #não tem campo no site
        data_unit = {"Site": "AgenciadeLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def portalzuk():
    # Iniciar o display virtual
    #display = Display(visible=0, size=(1024, 768))
    #display.start()

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1024, 768)
   
    # Abrir a página
    driver.get("https://www.portalzuk.com.br/leilao-de-imoveis")

    # Fechar o pop-up inicial se existir
    try:
        button_no = WebDriverWait(driver, 3).until(
            lambda d: d.find_element(By.CLASS_NAME, "modal-m-btn-close")
        )
        button_no.click()
    except TimeoutException:
        pass  # Se o botão não aparecer dentro de 3 segundos, continuar
    
    scroll_increment = 100
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Desce a página de 100 em 100 pixels
        driver.execute_script(f"window.scrollBy(0, {scroll_increment});")

        # Verifica se o botão 'Mais' está presente
        try:
            button_more = driver.find_element(By.CLASS_NAME, "btn.btn-outline.btn-xl")
            button_more.click()
            # Aguarda um momento para o conteúdo ser carregado após o clique
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.body.scrollHeight") > last_height
            )
            last_height = driver.execute_script("return document.body.scrollHeight")
        except:  # noqa: E722
            # Verifica se chegou ao fim da página
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
    # Obter o HTML da página após o carregamento do conteúdo
    html_content = driver.page_source

    # Fechar o driver
    driver.quit()

    # Criar e retornar o objeto BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    
    cards = soup.find("div", class_="list-items").find_all("div", class_="card-property card_lotes_div")
    print(len(cards))
    data = []
    for card in cards:
        link = card.find("div", class_="card-property-image-wrapper").find("a").get("href")
        img_cover = card.find("div", class_="card-property-image-wrapper").find("a").find("img").get("src")
        value = float(card.find("span", class_="card-property-price-value").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        soup = get_selenium(link)
        name = soup.find("div", class_="content").find("h1", class_="title").text.lstrip().rstrip()
        address = soup.find("div", class_="content").find("p", class_="property-address").text.replace("\n", " ").lstrip().rstrip()
        while "  " in address:
            address = address.replace("  ", " ")
            
        area_util = None
        area_total = None
        infos = soup.find("div", class_="property-featured-items").find_all("div", class_="property-featured-item")
        for info in infos:
            info = info.text
            if "construída" in info:
                area_util = info.split()[-1].split("construída")[1].lstrip().rstrip()
            elif "terreno" in info:
                area_total = info.split()[-1].split("terreno")[1].lstrip().rstrip()

        appraisal_value = None #site não tem campo

        data_unit = {"Site": "PortalZuk",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def superbid():
    # Configurar o driver do Selenium #trouxe o código aqui porque esse vale apena
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1024, 768)

    urls = ["https://www.superbid.net/categorias/imoveis/terrenos-e-lotes", 
            "https://www.superbid.net/categorias/imoveis/imoveis-industriais",
            "https://www.superbid.net/categorias/imoveis/imoveis-rurais",
            "https://www.superbid.net/categorias/imoveis/imoveis-comerciais",
            "https://www.superbid.net/categorias/imoveis/imoveis-residenciais",
            "https://www.superbid.net/categorias/carros-motos/carros",
            "https://www.superbid.net/categorias/carros-motos/partes-e-pecas-carros-e-motos",
            "https://www.superbid.net/categorias/carros-motos/motos",
            "https://www.superbid.net/categorias/embarcacoes-aeronaves/embarcacoes-e-navios",
            "https://www.superbid.net/categorias/embarcacoes-aeronaves/pecas-e-acessorios",
            "https://www.superbid.net/categorias/embarcacoes-aeronaves/helicopteros",
            "https://www.superbid.net/categorias/caminhoes-onibus/onibus",
            "https://www.superbid.net/categorias/caminhoes-onibus/partes-e-pecas-caminhoes-e-onibus",
            "https://www.superbid.net/categorias/caminhoes-onibus/caminhoes",
            "https://www.superbid.net/categorias/caminhoes-onibus/vans",
            "https://www.superbid.net/categorias/caminhoes-onibus/impl-rod-e-carrocerias",
            "https://www.superbid.net/categorias/maquinas-pesadas-agricolas/equip-de-pavimentacao",
            "https://www.superbid.net/categorias/maquinas-pesadas-agricolas/maquinas-pesadas",
            "https://www.superbid.net/categorias/maquinas-pesadas-agricolas/partes-e-pecas-maquinas-pesadas-e-agricolas",
            "https://www.superbid.net/categorias/maquinas-pesadas-agricolas/equip-de-mineracao",
            "https://www.superbid.net/categorias/maquinas-pesadas-agricolas/implementos-agricolas",
            "https://www.superbid.net/categorias/maquinas-pesadas-agricolas/maquinas-agricolas",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/ind-bens-de-consumo",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/hospitalares",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/ind-grafica",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/ind-moveleira",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/ind-de-alimentos",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/ind-eletronicos",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/tubulacoes-e-conexoes",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/ind-textil",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/ind-de-embalagens",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/construcao-civil",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/energia-usinas",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/ind-farmaceutica",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/serraria",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/ind-petro-quimico",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/ind-plastica",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/pecas-industriais",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/infraestrutura",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/laboratorios",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/equipos-de-limpieza",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/agronegocios",
            "https://www.superbid.net/categorias/industrial-maquinas-equipamentos/metal-mecanica",
            "https://www.superbid.net/categorias/movimentacao-transporte/transportadores",
            "https://www.superbid.net/categorias/movimentacao-transporte/equipamentos",
            "https://www.superbid.net/categorias/movimentacao-transporte/armazenagem",
            "https://www.superbid.net/categorias/movimentacao-transporte/empilhadeiras",
            "https://www.superbid.net/categorias/tecnologia/informatica",
            "https://www.superbid.net/categorias/tecnologia/telefonia",
            "https://www.superbid.net/categorias/tecnologia/eletronicos",
            "https://www.superbid.net/categorias/eletrodomesticos/refrigeradores",
            "https://www.superbid.net/categorias/eletrodomesticos/fornos-e-fogoes",
            "https://www.superbid.net/categorias/eletrodomesticos/eletroportateis",
            "https://www.superbid.net/categorias/eletrodomesticos/limpeza",
            "https://www.superbid.net/categorias/materiais-para-construcao-civil/ferramentas",
            "https://www.superbid.net/categorias/materiais-para-construcao-civil/materiais",
            "https://www.superbid.net/categorias/materiais-para-construcao-civil/eletrica-e-iluminacao",
            "https://www.superbid.net/categorias/cozinhas-e-restaurantes/restaurantes",
            "https://www.superbid.net/categorias/cozinhas-e-restaurantes/cozinhas-industriais",
            "https://www.superbid.net/categorias/moveis-e-decoracao/escritorio",
            "https://www.superbid.net/categorias/moveis-e-decoracao/residencial",
            "https://www.superbid.net/categorias/alimentos-e-bebidas/bebidas",
            "https://www.superbid.net/categorias/alimentos-e-bebidas/alimentos",
            "https://www.superbid.net/categorias/oportunidades/beneficentes",
            "https://www.superbid.net/categorias/oportunidades/papelaria",
            "https://www.superbid.net/categorias/oportunidades/pet",
            "https://www.superbid.net/categorias/oportunidades/negocios",
            "https://www.superbid.net/categorias/oportunidades/lazer",
            "https://www.superbid.net/categorias/oportunidades/vestuarios",
            "https://www.superbid.net/categorias/oportunidades/esportes",
            "https://www.superbid.net/categorias/bolsas-canetas-joias-e-relogios/bolsas",
            "https://www.superbid.net/categorias/bolsas-canetas-joias-e-relogios/acessorios",
            "https://www.superbid.net/categorias/bolsas-canetas-joias-e-relogios/relogios",
            "https://www.superbid.net/categorias/bolsas-canetas-joias-e-relogios/joias",
            "https://www.superbid.net/categorias/bolsas-canetas-joias-e-relogios/tabacaria",
            "https://www.superbid.net/categorias/artes-decoracao-colecionismo/pinturas",
            "https://www.superbid.net/categorias/artes-decoracao-colecionismo/obras-de-arte",
            "https://www.superbid.net/categorias/animais/equinos",
            "https://www.superbid.net/categorias/animais/bovinos",
            "https://www.superbid.net/categorias/sucatas-materiais-residuos/sucatas-materiais",
            "https://www.superbid.net/categorias/sucatas-materiais-residuos/residuos",
            "https://www.superbid.net/categorias/sucatas-materiais-residuos/pecas-componentes",
            "https://www.superbid.net/categorias/sucatas-materiais-residuos/sucatas-metalicas",
            "https://www.superbid.net/categorias/sucatas-materiais-residuos/materiais-metalicos",
            "https://www.superbid.net/categorias/sucatas-materiais-residuos/sucatas-nao-ferrosos",
            "https://www.superbid.net/categorias/sucatas-materiais-residuos/sucatas-equipamentos",
            "https://www.superbid.net/categorias/sucatas-materiais-residuos/materia-prima",
            "https://www.superbid.net/categorias/sucatas-materiais-residuos/mat-prod-quimicos",
            ]

    cards = []
    for url in urls:
        while True:
            try:
                driver.get(f"{url}?searchType=opened&pageNumber=1&pageSize=99999&orderBy=price:desc")
                # Rolar a página para carregar todo o conteúdo dinâmico
                last_height = driver.execute_script("return document.body.scrollHeight")

                while True:
                    # Rolar para baixo
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                    # Esperar o conteúdo carregar
                    try:
                        WebDriverWait(driver, 20).until(
                            lambda driver: driver.execute_script("return document.body.scrollHeight") > last_height
                        )
                    except TimeoutException:
                        break  # Se o tempo de espera exceder, sair do loop

                    # Atualizar a altura da página após o scroll
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height

                # Obter o HTML da página após o carregamento do conteúdo
                html_content = driver.page_source

                # Criar e retornar o objeto BeautifulSoup
                soup = BeautifulSoup(html_content, "html.parser")

                cards_page = soup.find_all("div", class_="MuiGrid-root MuiGrid-container MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-sm-5 MuiGrid-grid-md-3.1 css-1kam6io")
                for card in cards_page:
                    cards.append(card)
                cards_page = soup.find_all("div", class_="MuiGrid-root MuiGrid-container MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-sm-5 MuiGrid-grid-md-4 css-1gf6smk")
                for card in cards_page:
                    cards.append(card)
                break
            except:  # noqa: E722
                pass
    driver.quit()

    data = []
    for card in cards:
        link = f"https://www.superbid.net{card.find("div", class_="react-swipeable-view-container").find("a").get("href")}"
        img_cover = card.find("div", class_="react-swipeable-view-container").find("a").find("img").get("src")
        
        soup = get_selenium(link)
        os.system("cls")
        print(card)
        name = soup.find("div", class_="MuiGrid-root MuiGrid-container MuiGrid-item MuiGrid-grid-xs-12 jss170 css-h8rdph").find("div", class_="MuiGrid-root MuiGrid-container MuiGrid-item MuiGrid-grid-xs-12 css-11bs1r6").find("h1").text.lstrip().rstrip()
        address = soup.find("div", class_="MuiGrid-root MuiGrid-container MuiGrid-item MuiGrid-grid-xs-12 jss170 css-h8rdph").find("div", class_="MuiGrid-root MuiGrid-container MuiGrid-item MuiGrid-grid-xs-12 css-11bs1r6").find("h2").text.replace("Localização", " ").lstrip().rstrip()
        value = None
        try:
            infos = soup.find("div", class_="MuiGrid-root MuiGrid-container MuiGrid-direction-xs-column css-12g27go").find_all("div", class_="jss173")
            for info in infos:
                info = info.text
                if "Valor inicial" in info:
                    value = info
        except:  # noqa: E722
            pass
    
        if value is None or value == 0:
            try:
                value = soup.find("div", class_="MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation1 css-ay1ysm").find("p", class_="MuiTypography-root MuiTypography-body1 css-z355qp").text
            except:  # noqa: E722
                pass
        if value is None or value == 0:
            try:
                value = card.find("p", class_="MuiTypography-root MuiTypography-body1 jss313 css-z355qp").text
            except:  # noqa: E722
                pass

        if value is not None:
            if "R$" in value:
                value = float(value.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
            elif "U$" in value:
                value = float(value.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
                response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
                if response.status_code != 200:
                    return None
                value_dolar = response.json()["rates"]["BRL"]
                if value_dolar is None:
                    value = value
                else:
                    value = value * value_dolar
                
        descricao = soup.find("div", class_="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-md-12 MuiGrid-grid-lg-12 css-1ojex0").find("div", class_="jss172").text
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        appraisal_value = None # Site não tem o campo

        data_unit = {"Site": "SuperBid",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def tonialleiloes():
    cards = []
    
    urls = ["https://www.tonialleiloes.com.br/leilao/lotes/imoveis", "https://www.tonialleiloes.com.br/leilao/lotes/maquinas-1", "https://www.tonialleiloes.com.br/leilao/lotes/sucatas", "https://www.tonialleiloes.com.br/leilao/lotes/veiculos", "https://www.tonialleiloes.com.br/leilao/lotes/diversos", "https://www.tonialleiloes.com.br/leilao/lotes/animais", "https://www.tonialleiloes.com.br/venda-direta"]
    for url in urls:
        x=1
        while True:
            try:
                soup = get_requests(url)
                infos = soup.find_all("div", class_="row")
                for info in infos:
                    cards_page = info.find_all("div", class_="col-12 col-md-6 col-lg-4 col-xl-3")

                    if len(cards_page) > 0:
                        break
                for card in cards_page:
                    cards.append(card)
                url = f"https://www.tonialleiloes.com.br{soup.find("a", class_="page-link navigation__next").get("href")}"
                x+=1
            except:  # noqa: E722
                break

    data = []
    for card in cards:
        img_cover = None
        try:
            img_cover = card.find("div", class_="front").find("div", class_="carousel-inner").find("img").get("src")
        except:  # noqa: E722
            try:
                img_cover = card.find("div", class_="card-header card-header-image").find("img").get("src")
            except:  # noqa: E722
                pass
        link = None
        try:
            link = f"https://www.tonialleiloes.com.br{card.find("div", class_="back").find("div", class_="card-footer").find("a").get("href")}"
        except:  # noqa: E722
            link = f"https://www.tonialleiloes.com.br{card.find("div", class_="card-header card-header-image").find("a").get("href")}"
        soup = get_requests(link)
        name = soup.find("h4", class_="card-title").text.replace("\n", "").lstrip().rstrip()
        value = float(soup.find("p", class_="lance-inicial-valor").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        appraisal_value = None
        try:
            appraisal_value = float(soup.find("div", class_="card-body text-center").find("h4").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            pass
        descricao = None
        try:
            descricao = soup.find("div", class_="col-12 descricao").text
        except:  # noqa: E722
            pass
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        address = None #não tem campo no site
        data_unit = {"Site": "TonialLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def pimentelleiloes():
    urls = ["https://www.pimentelleiloes.com.br/lotes/imovel?tipo=imovel&page=", "https://www.pimentelleiloes.com.br/lotes/veiculo?tipo=veiculo&page=", "https://www.pimentelleiloes.com.br/lotes/diversos?tipo=diversos&page="]
    data = []
    cards = []
    for url in urls:
        soup = get_requests(url)
        links = []
        try:
            bar = soup.find("ul", class_="pagination justify-content-center")
            lis = bar.find_all("li", class_="page-item")
            numero_paginas = int(lis[-2].text)

            for x in range(numero_paginas):
                links.append(f"{url}{x+1}")

            for link in links:
                page = get_requests(link)
                cards_page = page.find_all("div", class_="lote")
                for card in cards_page:
                    cards.append(card)

        except:  # noqa: E722
            cards_page = soup.find_all("div", class_="lote")
            for card in cards_page:
                cards.append(card)

    for card in cards:
        img = card.find("div", class_="col-12 col-lg-2").find("a", class_="rounded").get("style")
        img = re.search(r"url\('([^']+)'\)", img)
        img_cover = img.group(1) if img else None

        name = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").find("h5").text
        
        info_div = card.find("div", class_="col-12 col-lg-7 text-justify")

        try:
            address = info_div.find("div").find("div").text.split('\n')
            for linha in address:
                if "Cidade:" in linha:
                    city1 = linha.split("Cidade:")

                    if len(city1) > 1:
                        city = city1[1].strip()
                        
                if "Endereço:" in linha:
                    address_p = linha.split("Endereço:")

                    if len(address_p) > 1:
                        address1 = address_p[1].strip().split('   ')[0]
                        break
            address = f"{address1}, {city}"
            
        except:  # noqa: E722
            address = None

        link = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").get("href")      
        if "https://www.pimentelleiloes" not in link:
            continue
        soup = get_requests(link)
        
        def extrair_valor(texto):
            if texto:
                match = re.search(r'R\$([\d\.]+,\d+)', texto)
                return match.group(1) if match else None
            return None

        # Encontrar todos os elementos <h6>
        h6_elements = soup.find_all('h6', class_="text-center border-top p-2 m-0")

        # Inicializando variáveis
        appraisal_value = None
        value1 = None
        value2 = None

        # Iterar sobre os elementos encontrados
        for element in h6_elements:
            if "Valor de Avaliação:" in element.text:
                appraisal_value = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
            elif "Lance Inicial:" in element.text:
                if value1 is None:
                    value1 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
                else:
                    value2 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))

        if value1 and value2 is not None:
            value = min(value1, value2)
        
        elif value1 is not None:
            value = value1

        elif value2 is not None:
            value = value2

        else:
            value = None

        descricao = soup.find("div", class_="mb-3 p-2 border rounded text-justify").find_all("div")[1].text
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "PimentelLeiloes",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link,
                        "Link imagem da capa": img_cover
                        }
        data.append(data_unit)
    return data

def leilaobrasil():
    soup = get_selenium("https://www.leilaobrasil.com.br/")
    cards = soup.find_all("div", class_="col-sm-6 col-md-4 col-lg-3 mb-4 leilao-home")

    data = []
    for card in cards:
        link = f"https://www.leilaobrasil.com.br/{card.find("a").get("href")}"
        infos = card.find("a").find("div", class_="imagem").find("span", class_="d-flex w-100").get("style").split(";")
        for info in infos:
            if "arquivos" in info:
                img_cover = f"https://www.leilaobrasil.com.br/{info.lstrip().rstrip()}"
        name = card.find("a").get("title")

        soup = get_requests(link)

        infos = soup.find_all("div", class_="border-bottom p-2")
        for info in infos:
            info = info.text
            if "Lance Inicial" in info:
                value = float(info.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

            elif "Valor do bem" in info:
                appraisal_value = float(info.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

            elif "Localização" in info:
                address = info.replace("Localização", " ").lstrip().rstrip()

        descricao = soup.find("div", id="descricao").text
        print(descricao)
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "LeilaoBrasil",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link,
                        "Link imagem da capa": img_cover
                        }
        data.append(data_unit)
    return data

def saraivaleiloes():
    urls = ["https://www.saraivaleiloes.com.br/categoria/Im%C3%B3veis", "https://www.saraivaleiloes.com.br/categoria/Apartamentos", "https://www.saraivaleiloes.com.br/categoria/Comercial", "https://www.saraivaleiloes.com.br/categoria/Materiais", "https://www.saraivaleiloes.com.br/categoria/Diversos", "https://www.saraivaleiloes.com.br/categoria/Ve%C3%ADculos"]
    cards = []

    for url in urls:
        soup = get_requests(url)
        cards_page = soup.find("div", class_="list-lotes lista").find_all("div", class_="lote")
        for card in cards_page:
            cards.append(card)

    data = []
    for card in cards:
        link = f"https://www.saraivaleiloes.com.br{card.find("a", class_="lote-image").get("href")}"
        print(link)
        imgs = card.find("a", class_="lote-image").find("div", class_="image").get("style").split(";")
        for img in imgs:
            if "http" in img:
                img_cover = img
                break
        name = card.find("h3").text.lstrip().rstrip()

        soup = get_requests(link)

        address = soup.find_all("div", class_="lote-texto")[-1].text.lstrip().rstrip()
        if address == "Não disponível.":
            address = None

        values = []
        values_d = soup.find_all("div", class_="stats valorAtual ml-0")
        for x in values_d:
            values.append(float(x.find("span").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.')))
        value = min(values)

        appraisal_value = float(soup.find("div", class_="stats ml-0").text.split("$")[1].split("\n")[0].lstrip().rstrip().replace('.', '').replace(',', '.'))

        descricao = soup.find("div", class_="item-descritivos")
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "LeilaoBrasil",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link,
                        "Link imagem da capa": img_cover
                        }
        data.append(data_unit)
    return data

def kleiloes():
    soup = get_requests("https://www.kleiloes.com.br/")
    cards_ini = soup.find("div", id="painel-leiloes-ativos").find_all("a", class_="box-leilao")
    
    cards = []
    for card in cards_ini:
        card = f"https://www.kleiloes.com.br/{card.get("href")}"
        soup = get_requests(card)

        try:
            cards_p = soup.find("table", class_="table table-bordered table-striped table-hover").find_all("tr")
            for card_t in cards_p:
                cards.append(card_t)
        except:  # noqa: E722
            pass

    data = []
    for card in cards:
        print(card)
        link = card.find("td", class_="NumLoteSublote")
        print(link)
        name = card.find("td", class_="DescLote").find("a").text.lstrip().rstrip()

        values = []
        value1 = float(card.find("td", class_="ValorPrimeiraPraca text-right").find("a").text)
        if value1 != 0:
            values.append(value1)
        value1 = float(card.find("td", class_="LanceMinimo text-right").find("a").text)
        if value1 != 0:
            values.append(value1)
        value = min(values)

        appraisal_value = float(card.find("td", class_="ValorAvaliacao text-right").find("a").text)

        soup = get_requests(link)
        img_cover = soup.find("div", class_="img-leilao").find("a").find("img").get("src")

        address = None
        try:
            address = soup.find("div", id="localizacao-leilao").text.replace("\n", " ").lstrip().rstrip()
            while "  " in address:
                address = address.replace("  ", " ")
        except:  # noqa: E722
            pass
        
        descricao = soup.find("span", id="ctl00_ContentPlaceHolder1_DescricaoCompletaSublote").text
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "KLeiloes",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link,
                        "Link imagem da capa": img_cover
                        }
        data.append(data_unit)
        print(data_unit)
        break
    return data

def kcleiloes():
    urls = ["https://www.kcleiloes.com.br/lotes/imovel&page=", "https://www.kcleiloes.com.br/lotes/veiculo?tipo=veiculo&page=", "https://www.kcleiloes.com.br/lotes/diversos?tipo=diversos&page="]
    data = []
    cards = []
    for url in urls:
        soup = get_requests(url)
        links = []
        try:
            bar = soup.find("ul", class_="pagination justify-content-center")
            lis = bar.find_all("li", class_="page-item")
            numero_paginas = int(lis[-2].text)

            for x in range(numero_paginas):
                links.append(f"{url}{x+1}")

            for link in links:
                page = get_requests(link)
                cards_page = page.find_all("div", class_="lote")
                for card in cards_page:
                    cards.append(card)

        except:  # noqa: E722
            cards_page = soup.find_all("div", class_="lote")
            for card in cards_page:
                cards.append(card)

    for card in cards:
        img = card.find("div", class_="col-12 col-lg-2").find("a", class_="rounded").get("style")
        img = re.search(r"url\('([^']+)'\)", img)
        img_cover = img.group(1) if img else None

        name = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").find("h5").text
        
        info_div = card.find("div", class_="col-12 col-lg-7 text-justify")

        try:
            address = info_div.find("div").find("div").text.split('\n')
            for linha in address:
                if "Cidade:" in linha:
                    city1 = linha.split("Cidade:")

                    if len(city1) > 1:
                        city = city1[1].strip()
                        
                if "Endereço:" in linha:
                    address_p = linha.split("Endereço:")

                    if len(address_p) > 1:
                        address1 = address_p[1].strip().split('   ')[0]
                        break
            address = f"{address1}, {city}"
            
        except:  # noqa: E722
            address = None

        link = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").get("href")      
        if "https://www.kcleiloes" not in link:
            continue
        soup = get_requests(link)
        
        def extrair_valor(texto):
            if texto:
                match = re.search(r'R\$([\d\.]+,\d+)', texto)
                return match.group(1) if match else None
            return None

        # Encontrar todos os elementos <h6>
        h6_elements = soup.find_all('h6', class_="text-center border-top p-2 m-0")

        # Inicializando variáveis
        appraisal_value = None
        value1 = None
        value2 = None

        # Iterar sobre os elementos encontrados
        for element in h6_elements:
            if "Valor de Avaliação:" in element.text:
                appraisal_value = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
            elif "Lance Inicial:" in element.text:
                if value1 is None:
                    value1 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
                else:
                    value2 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))

        if value1 and value2 is not None:
            value = min(value1, value2)
        
        elif value1 is not None:
            value = value1

        elif value2 is not None:
            value = value2

        else:
            value = None

        descricao = soup.find("div", class_="mb-3 p-2 border rounded text-justify").find_all("div")[-1].text
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "KCLeiloes",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link,
                        "Link imagem da capa": img_cover
                        }
        data.append(data_unit)
    return data

def patiorochaleiloes():
    urls = ["https://www.patiorochaleiloes.com.br/lotes/imovel?tipo=imovel&page=", "https://www.patiorochaleiloes.com.br/lotes/veiculo?tipo=veiculo&page=", "https://www.patiorochaleiloes.com.br/lotes/diversos?tipo=diversos&page="]
    data = []
    cards = []
    for url in urls:
        soup = get_requests(url)
        links = []
        try:
            bar = soup.find("ul", class_="pagination justify-content-center")
            lis = bar.find_all("li", class_="page-item")
            numero_paginas = int(lis[-2].text)

            for x in range(numero_paginas):
                links.append(f"{url}{x+1}")

            for link in links:
                page = get_requests(link)
                cards_page = page.find_all("div", class_="lote")
                for card in cards_page:
                    cards.append(card)

        except:  # noqa: E722
            cards_page = soup.find_all("div", class_="lote")
            for card in cards_page:
                cards.append(card)

    for card in cards:
        img = card.find("div", class_="col-12 col-lg-2").find("a", class_="rounded").get("style")
        img = re.search(r"url\('([^']+)'\)", img)
        img_cover = img.group(1) if img else None

        name = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").find("h5").text
        
        info_div = card.find("div", class_="col-12 col-lg-7 text-justify")

        try:
            address = info_div.find("div").find("div").text.split('\n')
            for linha in address:
                if "Cidade:" in linha:
                    city1 = linha.split("Cidade:")

                    if len(city1) > 1:
                        city = city1[1].strip()
                        
                if "Endereço:" in linha:
                    address_p = linha.split("Endereço:")

                    if len(address_p) > 1:
                        address1 = address_p[1].strip().split('   ')[0]
                        break
            address = f"{address1}, {city}"
            
        except:  # noqa: E722
            address = None

        link = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").get("href")      
        if "https://www.patiorochaleiloes" not in link:
            continue
        soup = get_requests(link)
        
        def extrair_valor(texto):
            if texto:
                match = re.search(r'R\$([\d\.]+,\d+)', texto)
                return match.group(1) if match else None
            return None

        # Encontrar todos os elementos <h6>
        h6_elements = soup.find_all('h6', class_="text-center border-top p-2 m-0")

        # Inicializando variáveis
        appraisal_value = None
        value1 = None
        value2 = None

        # Iterar sobre os elementos encontrados
        for element in h6_elements:
            if "Valor de Avaliação:" in element.text:
                appraisal_value = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
            elif "Lance Inicial:" in element.text:
                if value1 is None:
                    value1 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
                else:
                    value2 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))

        if value1 and value2 is not None:
            value = min(value1, value2)
        
        elif value1 is not None:
            value = value1

        elif value2 is not None:
            value = value2

        else:
            value = appraisal_value

        descricao = soup.find("div", class_="mb-3 p-2 border rounded text-justify").find_all("div")[-1].text
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "PatioRochaLeiloes",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link,
                        "Link imagem da capa": img_cover
                        }
        data.append(data_unit)
    return data

def ccjleiloes():
    urls = ["https://ccjleiloes.com.br/lotes/imovel&page=", "https://ccjleiloes.com.br/lotes/veiculo?tipo=veiculo&page=", "https://ccjleiloes.com.br/lotes/diversos?tipo=diversos&page="]
    data = []
    cards = []
    for url in urls:
        soup = get_requests(url)
        links = []
        try:
            bar = soup.find("ul", class_="pagination justify-content-center")
            lis = bar.find_all("li", class_="page-item")
            numero_paginas = int(lis[-2].text)

            for x in range(numero_paginas):
                links.append(f"{url}{x+1}")

            for link in links:
                page = get_requests(link)
                cards_page = page.find_all("div", class_="lote")
                for card in cards_page:
                    cards.append(card)

        except:  # noqa: E722
            cards_page = soup.find_all("div", class_="lote")
            for card in cards_page:
                cards.append(card)

    for card in cards:
        img = card.find("div", class_="col-12 col-lg-2").find("a", class_="rounded").get("style")
        img = re.search(r"url\('([^']+)'\)", img)
        img_cover = img.group(1) if img else None

        name = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").find("h5").text
        
        info_div = card.find("div", class_="col-12 col-lg-7 text-justify")

        try:
            address = info_div.find("div").find("div").text.split('\n')
            for linha in address:
                if "Cidade:" in linha:
                    city1 = linha.split("Cidade:")

                    if len(city1) > 1:
                        city = city1[1].strip()
                        
                if "Endereço:" in linha:
                    address_p = linha.split("Endereço:")

                    if len(address_p) > 1:
                        address1 = address_p[1].strip().split('   ')[0]
                        break
            address = f"{address1}, {city}"
            
        except:  # noqa: E722
            address = None

        link = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").get("href")      
        if "https://ccjleiloes" not in link:
            continue
        soup = get_requests(link)
        
        def extrair_valor(texto):
            if texto:
                match = re.search(r'R\$([\d\.]+,\d+)', texto)
                return match.group(1) if match else None
            return None

        # Encontrar todos os elementos <h6>
        h6_elements = soup.find_all('h6', class_="text-center border-top p-2 m-0")

        # Inicializando variáveis
        appraisal_value = None
        value1 = None
        value2 = None

        # Iterar sobre os elementos encontrados
        for element in h6_elements:
            if "Valor de Avaliação:" in element.text:
                appraisal_value = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
            elif "Lance Inicial:" in element.text:
                if value1 is None:
                    value1 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
                else:
                    value2 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))

        if value1 and value2 is not None:
            value = min(value1, value2)
        
        elif value1 is not None:
            value = value1

        elif value2 is not None:
            value = value2

        else:
            value = appraisal_value

        descricao = soup.find("div", class_="mb-3 p-2 border rounded text-justify").find_all("div")[-1].text
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "CCJLeiloes",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link,
                        "Link imagem da capa": img_cover
                        }
        data.append(data_unit)
    return data

def faleiloes():
    urls = ["https://faleiloes.com.br/lotes/imovel?tipo=imovel&page=", "https://faleiloes.com.br/lotes/veiculo?tipo=veiculo&page=", "https://faleiloes.com.br/lotes/diversos?tipo=diversos&page="]
    data = []
    cards = []
    for url in urls:
        soup = get_requests(url)
        links = []
        try:
            bar = soup.find("ul", class_="pagination justify-content-center")
            lis = bar.find_all("li", class_="page-item")
            numero_paginas = int(lis[-2].text)

            for x in range(numero_paginas):
                links.append(f"{url}{x+1}")

            for link in links:
                page = get_requests(link)
                cards_page = page.find_all("div", class_="lote")
                for card in cards_page:
                    cards.append(card)

        except:  # noqa: E722
            cards_page = soup.find_all("div", class_="lote")
            for card in cards_page:
                cards.append(card)

    for card in cards:
        img = card.find("div", class_="col-12 col-lg-2").find("a", class_="rounded").get("style")
        img = re.search(r"url\('([^']+)'\)", img)
        img_cover = img.group(1) if img else None

        name = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").find("h5").text
        
        info_div = card.find("div", class_="col-12 col-lg-7 text-justify")

        try:
            address = info_div.find("div").find("div").text.split('\n')
            for linha in address:
                if "Cidade:" in linha:
                    city1 = linha.split("Cidade:")

                    if len(city1) > 1:
                        city = city1[1].strip()
                        
                if "Endereço:" in linha:
                    address_p = linha.split("Endereço:")

                    if len(address_p) > 1:
                        address1 = address_p[1].strip().split('   ')[0]
                        break
            address = f"{address1}, {city}"
            
        except:  # noqa: E722
            address = None

        link = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").get("href")      
        if "https://faleiloes" not in link:
            continue
        soup = get_requests(link)
        
        def extrair_valor(texto):
            if texto:
                match = re.search(r'R\$([\d\.]+,\d+)', texto)
                return match.group(1) if match else None
            return None

        # Encontrar todos os elementos <h6>
        h6_elements = soup.find_all('h6', class_="text-center border-top p-2 m-0")

        # Inicializando variáveis
        appraisal_value = None
        value1 = None
        value2 = None

        # Iterar sobre os elementos encontrados
        for element in h6_elements:
            if "Valor de Avaliação:" in element.text:
                appraisal_value = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
            elif "Lance Inicial:" in element.text:
                if value1 is None:
                    value1 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
                else:
                    value2 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))

        if value1 and value2 is not None:
            value = min(value1, value2)
        
        elif value1 is not None:
            value = value1

        elif value2 is not None:
            value = value2

        else:
            value = appraisal_value

        descricao = soup.find("div", class_="mb-3 p-2 border rounded text-justify").find_all("div")[-1].text
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "FaLeiloes",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link,
                        "Link imagem da capa": img_cover
                        }
        data.append(data_unit)
    return data

def leilaopernambuco():
    urls = ["https://www.leilaopernambuco.com.br/lotes/imovel?tipo=imovel&page=", "https://www.leilaopernambuco.com.br/lotes/veiculo?tipo=veiculo&page=", "https://www.leilaopernambuco.com.br/lotes/diversos?tipo=diversos&page="]
    data = []
    cards = []
    for url in urls:
        soup = get_requests(url)
        links = []
        try:
            bar = soup.find("ul", class_="pagination justify-content-center")
            lis = bar.find_all("li", class_="page-item")
            numero_paginas = int(lis[-2].text)

            for x in range(numero_paginas):
                links.append(f"{url}{x+1}")

            for link in links:
                page = get_requests(link)
                cards_page = page.find_all("div", class_="lote")
                for card in cards_page:
                    cards.append(card)

        except:  # noqa: E722
            cards_page = soup.find_all("div", class_="lote")
            for card in cards_page:
                cards.append(card)

    for card in cards:
        img = card.find("div", class_="col-12 col-lg-2").find("a", class_="rounded").get("style")
        img = re.search(r"url\('([^']+)'\)", img)
        img_cover = img.group(1) if img else None

        name = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").find("h5").text
        
        info_div = card.find("div", class_="col-12 col-lg-7 text-justify")

        try:
            address = info_div.find("div").find("div").text.split('\n')
            for linha in address:
                if "Cidade:" in linha:
                    city1 = linha.split("Cidade:")

                    if len(city1) > 1:
                        city = city1[1].strip()
                        
                if "Endereço:" in linha:
                    address_p = linha.split("Endereço:")

                    if len(address_p) > 1:
                        address1 = address_p[1].strip().split('   ')[0]
                        break
            address = f"{address1}, {city}"
            
        except:  # noqa: E722
            address = None

        link = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").get("href")      
        if "https://www.leilaopernambuco" not in link:
            continue
        soup = get_requests(link)
        
        def extrair_valor(texto):
            if texto:
                match = re.search(r'R\$([\d\.]+,\d+)', texto)
                return match.group(1) if match else None
            return None

        # Encontrar todos os elementos <h6>
        h6_elements = soup.find_all('h6', class_="text-center border-top p-2 m-0")

        # Inicializando variáveis
        appraisal_value = None
        value1 = None
        value2 = None

        # Iterar sobre os elementos encontrados
        for element in h6_elements:
            if "Valor de Avaliação:" in element.text:
                appraisal_value = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
            elif "Lance Inicial:" in element.text:
                if value1 is None:
                    value1 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
                else:
                    value2 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))

        if value1 and value2 is not None:
            value = min(value1, value2)
        
        elif value1 is not None:
            value = value1

        elif value2 is not None:
            value = value2

        else:
            value = appraisal_value

        descricao = soup.find("div", class_="mb-3 p-2 border rounded text-justify").find_all("div")[-1].text
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "LeilaoPernambuco",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link,
                        "Link imagem da capa": img_cover
                        }
        data.append(data_unit)
    return data

def nsleiloes():
    cards = []
    
    urls = ["https://www.nsleiloes.lel.br/leilao/lotes/animais", "https://www.nsleiloes.lel.br/leilao/lotes/diversos", "https://www.nsleiloes.lel.br/leilao/lotes/eletronicos", "https://www.nsleiloes.lel.br/leilao/lotes/equipamentos", "https://www.nsleiloes.lel.br/leilao/lotes/imoveis", "https://www.nsleiloes.lel.br/leilao/lotes/maquinas", "https://www.nsleiloes.lel.br/leilao/lotes/sucatas", "https://www.nsleiloes.lel.br/leilao/lotes/veiculos", "https://www.nsleiloes.lel.br/venda-direta"]
    for url in urls:
        try:
            soup = get_requests(url)
            cards_page = soup.find_all("div", class_="col-12 col-md-6 col-lg-4 col-xl-3")
            for card in cards_page:
                cards.append(card)
        except:  # noqa: E722
            break

    data = []
    for card in cards:
        try:
            link = f"https://www.nsleiloes.lel.br{card.find("div", class_="back").find("div", class_="card-footer").find("a").get("href")}"
            img_cover = card.find("div", class_="front").find("div", class_="carousel-inner").find("img").get("src")
        except:  # noqa: E722
            try:
                link = f"https://www.nsleiloes.lel.br{card.find("div", class_="card-header card-header-image").find("a").get("href")}"
                img_cover = card.find("div", class_="card-header card-header-image").find("img").get("src")
            except: # noqa: E722
                link = f"https://www.nsleiloes.lel.br{card.find("div", class_="back").find("div", class_="card-footer").find("a").get("href")}"
                img_cover = f"https://www.nsleiloes.lel.br{card.find("div", class_="front").find("img").get("src")}"
        soup = get_requests(link)
        name = soup.find("h4", class_="card-title").text.replace("\n", "").lstrip().rstrip()
        value = float(soup.find("p", class_="lance-inicial-valor").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        appraisal_value = None
        try:
            appraisal_value = float(soup.find("div", class_="card-body text-center").find("h4").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            pass
        descricao = soup.find("div", class_="col-12 descricao").text
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        address = None #não tem campo no site
        data_unit = {"Site": "NSLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def nasarleiloes():
    soup = get_requests("https://www.nasarleiloes.com.br/#")
    urls = soup.find("div", id="proximos").find_all("article", class_="col-md-3 col-sm-6")

    cards = []
    for url in urls:
        tipo = url.find("div", class_="bid-lotes").find("p").get_text()
        tipo = int(''.join(filter(str.isdigit, tipo)))
        name = url.find("div", class_="bid-details").find("p", class_="bid-description").text.lstrip().rstrip()
        url = url.find("div", class_="bid-link").find("a").get("href")
        if "https://www.nasarleiloes" not in url:
            url = f"https://www.nasarleiloes.com.br{url}"
        if tipo == 1:
            url1 = {"url": url, "name": name}
            cards.append(url1)
        elif tipo > 1:
            soup = get_requests(url)
            cards_page = soup.find_all("div", class_="row box-lotes")
            for card in cards_page:
                links = card.find_all("a", class_="btn-list")
                name1 = card.find("div", class_="col-sm-6 infos-lote").find("div", class_="info-line").find("p").text.lstrip().rstrip()
                url_2 = None
                for link in links:
                    if "Mais detalhes" in link.text:
                        url_2 = link.get("href")
                        break
                if url_2 is not None:
                    url2 = {"url": url_2, "name": name1}
                    cards.append(url2)
    data = []
    for index, url in enumerate(cards):
        time.sleep(index/10)
        card = get_requests(url["url"])
        try:
            name = card.find("div", class_="title-lote").find("h2").text.lstrip().rstrip()
        except:  # noqa: E722
            name = url["name"]
        link = url["url"]
        img_cover = card.find("div", class_="col-imagens-lote").find("img").get("src")

        values = []
        infos = card.find("div", class_="col-sm-6 lote-details").find_all("div", class_="info-line clearfix")
        for info in infos:
            info = info.text

            if "Avaliação:" in info:
                appraisal_value = float(info.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
            
            elif "Lance inicial:" in info:
                values.append(float(info.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.')))
        
            elif "Localização:" in info:
                address = info.replace("Localização:", " ").replace("\n", " ")
                while "  " in address:
                    address = address.replace("  ", " ")

        if values is not None:
            value = min(values)
        else:
            value = None

        descricao = None
        info = card.find_all("div", class_="col-sm-8")[2]
        partes = []

        for child in info.descendants:
            partes.append(child.text)
        descricao = " ".join(partes)

        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "NasarLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def pecinileiloes():
    soup = get_selenium("https://www.pecinileiloes.com.br/busca/#Engine=Start&Pagina=1&RangeValores=0&OrientacaoBusca=0&Busca=&Mapa=&ID_Categoria=0&ID_Estado=-1&ID_Cidade=-1&Bairro=-1&ID_Regiao=0&ValorMinSelecionado=0&ValorMaxSelecionado=0&Ordem=0&QtdPorPagina=9999999&ID_Leiloes_Status=1&SubStatus=&PaginaIndex=3&BuscaProcesso=&NomesPartes=&CodLeilao=&TiposLeiloes=[]&CFGs=[]")
    cards = soup.find_all("div", class_="col-xs-12 col-sm-6 col-md-4 col-lg-3 dg-leiloes-item-col")
    
    data = []
    for card in cards:
        link = card.find("div", class_="dg-leiloes-lista-img").find("a", class_="dg-leiloes-img").get("href")
        imgs = card.find("div", class_="dg-leiloes-lista-img").find("a", class_="dg-leiloes-img").find("span").get("style").split("(")
        for img in imgs:
            if "http" in img:
                img_cover = img.split(")")[0]
        
        values = []
        value1 = float(card.find("span", class_="ValorMinimoLancePrimeiraPraca").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        if value1 != 0 and value1 != 0.00:
            values.append(value1)
        value1 = float(card.find("span", class_="ValorMinimoLanceSegundaPraca").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        if value1 != 0 and value1 != 0.00:
            values.append(value1)
        value1 = float(card.find("span", class_="ValorMinimoLanceTerceiraPraca").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        if value1 != 0 and value1 != 0.00:
            values.append(value1)
        value = min(values)

        soup = get_requests(link)
        info = soup.find("div", class_="dg-lote-descricao-txt")
        partes = []

        for child in info.descendants:
            partes.append(child.text)
        descricao = "\n".join(partes)

        name = soup.find("h1", class_="dg-lote-titulo").text.replace("\n", " ").replace("\r", " ")
        while "  " in name:
            name = name.replace("  ", " ")

        address = None
        try:
            address = soup.find("div", class_="dg-lote-local-endereco").text.lstrip().rstrip()
        except:  # noqa: E722
            pass
        
        appraisal_value = None
        try:
            infos = descricao.split("\n")
            for info in infos:
                if "Valor de Avaliação:" in info or "AVALIAÇÃO:" in info:
                    try:
                        appraisal_value = float(info.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
                    except:  # noqa: E722
                        pass
        except:  # noqa: E722
            appraisal_value = max(values)

        if appraisal_value is None or appraisal_value == 0:
            appraisal_value = max(values)

        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "PeciniLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def montenegroleiloes():
    urls = []
    soup = get_requests("https://www.montenegroleiloes.com.br/")
    urls_page = soup.find_all("div", class_="col-md-4 col-sm-6 col-xs-6 wrap-item")
    for url in urls_page:
        urls.append(url.find("div", class_="image").find("a").get("href"))

    cards = []
    for url in urls:
        soup = get_requests(url)
        cards_page = soup.find_all("div", class_="col-md-3 col-sm-6")
        for card in cards_page:
            cards.append(card)
    
    data = []
    for card in cards:
        link = f"https://www.montenegroleiloes.com.br{card.find("div", class_="image").find("a").get("href")}"
        img_cover = card.find("div", class_="image").find("a").find("img").get("src")
        name = card.find("div", class_="infos").find("h3").text.lstrip().rstrip()
        value = float(card.find("div", class_="control").find("span", class_="valor").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))

        soup = get_requests(link)

        info = soup.find("div", class_="observations")
        partes = []

        for child in info.descendants:
            partes.append(child.text)
        descricao = "\n".join(partes)

        address = None #site não tem campo mas aparece em algumas descrições
        infos = descricao.split("\n")
        for info in infos:
            if "localização:" in info:
                address = info.lstrip().rstrip()
        
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        appraisal_value = None #site não a informação

        data_unit = {"Site": "MontenegroLeiloes",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data

def agostinholeiloes():
    urls = ["https://www.agostinholeiloes.com.br/lotes/imovel?tipo=imovel&page=", "https://www.agostinholeiloes.com.br/lotes/veiculo?tipo=veiculo&page=", "https://www.agostinholeiloes.com.br/lotes/diversos?tipo=diversos&page="]
    data = []
    cards = []
    for url in urls:
        soup = get_requests(url)
        links = []
        try:
            bar = soup.find("ul", class_="pagination justify-content-center")
            lis = bar.find_all("li", class_="page-item")
            numero_paginas = int(lis[-2].text)

            for x in range(numero_paginas):
                links.append(f"{url}{x+1}")

            for link in links:
                page = get_requests(link)
                cards_page = page.find_all("div", class_="lote")
                for card in cards_page:
                    cards.append(card)

        except:  # noqa: E722
            cards_page = soup.find_all("div", class_="lote")
            for card in cards_page:
                cards.append(card)

    for card in cards:
        img = card.find("div", class_="col-12 col-lg-2").find("a", class_="rounded").get("style")
        img = re.search(r"url\('([^']+)'\)", img)
        img_cover = img.group(1) if img else None

        name = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").find("h5").text
        
        info_div = card.find("div", class_="col-12 col-lg-7 text-justify")

        try:
            address = info_div.find("div").find("div").text.split('\n')
            for linha in address:
                if "Cidade:" in linha:
                    city1 = linha.split("Cidade:")

                    if len(city1) > 1:
                        city = city1[1].strip()
                        
                if "Endereço:" in linha:
                    address_p = linha.split("Endereço:")

                    if len(address_p) > 1:
                        address1 = address_p[1].strip().split('   ')[0]
                        break
            address = f"{address1}, {city}"
            
        except:  # noqa: E722
            address = None

        link = card.find("div", class_="col-12 col-lg-7 text-justify").find("a").get("href")      
        if "https://www.agostinholeiloes" not in link:
            continue
        soup = get_requests(link)
        
        def extrair_valor(texto):
            if texto:
                match = re.search(r'R\$([\d\.]+,\d+)', texto)
                return match.group(1) if match else None
            return None

        # Encontrar todos os elementos <h6>
        h6_elements = soup.find_all('h6', class_="text-center border-top p-2 m-0")

        # Inicializando variáveis
        appraisal_value = None
        value1 = None
        value2 = None

        # Iterar sobre os elementos encontrados
        for element in h6_elements:
            if "Valor de Avaliação:" in element.text:
                appraisal_value = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
            elif "Lance Inicial:" in element.text:
                if value1 is None:
                    value1 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))
                else:
                    value2 = float(extrair_valor(element.text).replace('.', '').replace(',', '.'))

        if value1 and value2 is not None:
            value = min(value1, value2)
        
        elif value1 is not None:
            value = value1

        elif value2 is not None:
            value = value2

        else:
            value = appraisal_value

        descricao = soup.find("div", class_="mb-3 p-2 border rounded text-justify").find_all("div")[-1].text
        areas = get_areas(descricao)

        area_util = areas[0]
        area_total = areas[1]

        data_unit = {"Site": "AgostinhoLeiloes",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link,
                        "Link imagem da capa": img_cover
                        }
        data.append(data_unit)
    return data

def eleiloero():
    urls = ["https://www.e-leiloeiro.com.br/busca?tipo=im%C3%B3veis", "https://www.e-leiloeiro.com.br/busca?tipo=m%C3%A1quinas%20&%20equipamentos%20industriais", "https://www.e-leiloeiro.com.br/busca?tipo=bens%20diversos", "https://www.e-leiloeiro.com.br/busca?tipo=ve%C3%ADculos", "https://www.e-leiloeiro.com.br/busca?tipo=agro", ]
    
    cards = []
    for url in urls:
        soup = get_requests(url)
        cards_page = soup.find_all("div", class_="item-list lote-item")
        for card in cards_page:
            cards.append(card)
        
    data = []
    for card in cards:
        os.system("cls")
        print(card)
        link = f"https://www.e-leiloeiro.com.br{card.find("a", class_="column-11-copy w-col w-col-3 lote-thumb").get("href")}"
        imgs = card.find("a", class_="column-11-copy w-col w-col-3 lote-thumb").get("style").split(";")
        for img in imgs:
            if "http" in img:
                img_cover = img.split("&")[0]

        name = card.find("h5", class_="heading-5-copy").text.lstrip().rstrip()
        appraisal_value  = None
        try:
            appraisal_value = float(card.find("div", class_="w-col w-col-4").find("span", class_="text-span-2").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
        except:  # noqa: E722
            try:
                appraisal_value = float(card.find("div", class_="w-col w-col-4").find("span", class_="text-span-1").text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.'))
            except:  # noqa: E722
                pass
        if appraisal_value == 0 or appraisal_value == 0.0:
            appraisal_value = None

        soup = get_requests(link)

        values = []
        try:
            values_spans = soup.find_all("span", class_="text-span-7")
            for value_span in values_spans:
                values.append(float(value_span.text.split("$")[1].lstrip().rstrip().replace('.', '').replace(',', '.')))
        except:  # noqa: E722
            values_spans = soup.find_all("span", class_="text-span-2")
        
        if values:
            value = min(values)
        else:
            value = None
        
        address = soup.find("div", class_="text-block-18").find("a").text.lstrip().rstrip().replace("\n", " ")
        while "  " in address:
            address = address.replace("  ", " ")

        info = soup.find("p", class_="paragraph-3")
        partes = []

        for child in info.descendants:
            partes.append(child.text)
        descricao = "\n".join(partes)

        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1] 

        data_unit = {"Site": "ELeiloeiro",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link,
                        "Link imagem da capa": img_cover
                        }
        data.append(data_unit)
    return data

def sfrazao():
    soup = get_requests("https://sfrazao.com.br/pesquisa.php?classificacao=&uf=&cidade=&bairro=")
    cards = soup.find_all("div", class_="col-md-6 col-lg-3 mb-4")

    data = []
    for card in cards:
        link = 
        img_cover = 
        name = 

        appraisal_value = 
        value = 

        soup = get_requests(link)
        descricao = 
        areas = get_areas(descricao)
        area_util = areas[0]
        area_total = areas[1]

        address = 

        data_unit = {"Site": "SFrazao",
                    "Nome": name,
                    "Endereço": address,
                    "Área Útil": area_util,
                    "Área Total": area_total,
                    "Valor": value,
                    "Valor da Avaliação": appraisal_value,
                    "Link oferta": link,
                    "Link imagem da capa": img_cover
                    }
        data.append(data_unit)
    return data




if __name__ == "__main__":
    #controle
    os.system("cls")
    #mullerleiloes() 1
    #lancese() 2
    #francoleiloes() 3
    #leilaosantos() 4
    #leiloeirobonatto() 5
    #lessaleiloes() - VER - não tem leilao e nem categoria
    #rymerleiloes() 6
    #grupolance() 7
    #megaleiloes() 8
    #vivaleiloes() 9
    #biasileiloes() 10
    #sanchesleiloes() 11
    #grandesleiloes() 12
    #lancecertoleiloes() 13
    #hastapublica() 14
    #leiloes123() 15
    #moraesleiloes() 16
    #oleiloes() 17
    #stefanellileiloes() 18
    #globoleiloes() 19
    #veronicaleiloes() 20
    #delltaleiloes() 21
    #krobelleiloes() 22
    #mazzollileiloes() 23
    #oesteleiloes() 24
    #nordesteleiloes() 25
    #portellaleiloes() 26
    #rochaleiloes() 27
    #centraljudicial() 28
    #simonleiloes() 29
    #nogarileiloes() 30
    #trileiloes() 31
    #alfaleiloes() 32
    #wspleiloes() 33
    #fidalgoleiloes() 34
    #damianileiloes() 35
    #joaoemilio() 36
    #cravoleiloes() 37
    #topleiloes() 38
    #valerioiaminleiloes() 39
    #renovarleiloes() 40
    #agenciadeleiloes() 41
    #portalzuk() 42
    #superbid() 43
    #tonialleiloes() 44
    #pimentelleiloes() 45
    #leilaobrasil() 46
    #saraivaleiloes() 47
    #kleiloes() - Não funciona
    #kcleiloes() 48
    #patiorochaleiloes() 49
    #ccjleiloes() 50
    #faleiloes() 51
    #leilaopernambuco() 52
    #nsleiloes() 53
    #nasarleiloes() 54
    #pecinileiloes() 55
    #montenegroleiloes() 56
    #agostinholeiloes() 57
    #eleiloero() 58
    sfrazao()






