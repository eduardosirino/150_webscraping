from httpx import get
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
import credenciais

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
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)  # Espera para o conteúdo carregar
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

    soup = get_selenium(url="http://www.mullerleiloes.com.br/")
    
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
            value1, value2 = values[0].replace("R$", ""), values[1].replace("R$", "")
            value = min(value1, value2)
        except:  # noqa: E722
            infos3 = infos2.find_all("h6", class_="text-center border-top p-2 m-0")
            for info in infos3:
                linhas = info.text.split('\n')
                for linha in linhas:
                    if "Lance Inicial:" in linha:
                        value1 = linha.split("Lance Inicial:")

                        if len(value1) > 1:
                            value = value1[1].strip().replace("R$", "")
        
        appraisal_value = None
        try:
            for info in infos2:
                linhas = info.get_text().split('\n')
                for linha in linhas:
                    if "Valor de Avaliação:" in linha:
                        value1 = linha.split("Valor de Avaliação:")
                        if len(value1) > 1:
                            appraisal_value = value1[1].strip().replace("R$", "")
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
    urls = ["https://lancese.com.br/lotes/imovel", "https://lancese.com.br/lotes/veiculo", "https://lancese.com.br/lotes/diversos"]
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
                appraisal_value = extrair_valor(element.text)
            elif "Lance Inicial:" in element.text:
                if value1 is None:
                    value1 = extrair_valor(element.text)
                else:
                    value2 = extrair_valor(element.text)

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
                        "Valor": value.replace("R$", ""),
                        "Valor da Avaliação": appraisal_value.replace("R$", ""),
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
                value0 = value0.split("$")[1]
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
    soup = get_requests("https://leilaosantos.com.br/")

    links = []
    cards = soup.find_all("div", class_="col-md-6 col-lg-4 col-xl-3 p-2")
    for card in cards:
        link = card.find("div", class_="card-body d-flex flex-column").find("a").get("href")
        links.append(link)
    
    data = []
    for link in links:
        soup = get_requests(link)
        cards = soup.find_all("div", class_="lote")

        for card in cards:
            link2 = card.find("div", class_="col-12 col-lg-2").find("a").get("href")
            img = card.find("div", class_="col-12 col-lg-2").find("a", class_="rounded").get("style")
            img = re.search(r"url\('([^']+)'\)", img)
            img_cover = img.group(1) if img else None
            name1 = card.find("div", class_="col-12 col-lg-7 text-justify").find("a", href=link2).find("h5").text
            descricao = card.find("div", class_="col-12 col-lg-7 text-justify").find("p", class_="mb-0").text
            descricao = ", ".join(descricao.split())
            name = f"{name1} - {descricao}"
            address = card.find("div", class_="col-12 col-lg-7 text-justify").find("a", href=link2).find("div").find("div").text.split(":")[1].lstrip()
            
            soup2 = get_requests(link2)
            
            value = soup2.find("div", "col-12 col-lg-4 float-right p-1").find_all("div", class_="my-2 p-2 border rounded text-center")[2].find_all("h6", class_="text-center border-top p-2 m-0")[1].text.split(":")[1].lstrip().replace("R$", "")

            area_util = None # Não tem nenhum imóvel nesse site
            area_total = None # Não tem nenhum imóvel nesse site
            appraisal_value = None # Não tem nenhum imóvel nesse site

            data_unit = {"Site": "LeilaoSantos",
                        "Nome": name,
                        "Endereço": address,
                        "Área Útil": area_util,
                        "Área Total": area_total,
                        "Valor": value,
                        "Valor da Avaliação": appraisal_value,
                        "Link oferta": link2,
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
                value1 = linha.split("$")[1].lstrip()

            elif "2ª" or "2º" in linha:
                value2 = linha.split("$")[1].lstrip()

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
                appraisal_value = info.split("$")[1].split("(")[0].lstrip().rstrip()
     

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
                img_cover = info.find("div", style="overflow: hidden;").find("a").find("img").get("src")

        soup = get_selenium(link)

        name = soup.find("h1", class_="MuiTypography-root MuiTypography-h1 jss268 jss184 css-1yomz3x").text

        address = soup.find("h2", class_="MuiTypography-root MuiTypography-h2 jss183 css-1d9jgx0")
        infos = soup.find("div", class_="MuiGrid-root MuiGrid-container MuiGrid-direction-xs-column css-12g27go").find_all("span", class_="jss173").text
        for info in infos:
            if "R$" in info:
                print(info)
        texts = soup.find("div", class_="jss172").get_text().split("\n")
        for text in texts:
            if "avaliação:" in text.lower() or "atualizada:" in text.lower():
                appraisal_value = text.split("$").split("(").lstrip().rstrip()
            elif "segundo leilão" in text:
                value2 = text.split("$").split("(").lstrip().rstrip()
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
        address = card.find("section").find("div", class_="wrapp-infos-leilao").find("div", class_="col-lista-descricao").find("div", class_="descricao").find("a").text
        value1 = card.find("section").find("div", class_="box-info-leilao").find_all("div", class_="linha linha-praca-1 active")[1].find("span").text.split("$")[1].lstrip().rstrip()
        
        value2 = None
        try:
            value2 = card.find("section").find("div", class_="box-info-leilao").find_all("div", class_="linha linha-praca-1 {M:CLASS_IS_ATIVO_2}")[1].find("span").text.split("$").lstrip().rstrip()
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

        appraisal_value = soup.find("div", "col-info-lote-2").find("div", "linha-info").text.split("$")[1].lstrip().rsplit()[0]

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
    soup = get_requests("https://www.grupolance.com.br/Pesquisa")
    quant_pages = soup.find("li", class_="page-item last").find("a", class_="page-link").get("href").split("=")[1]
    
    data = []
    cards = []
    for x in range(int(quant_pages)):
        page = f"https://www.grupolance.com.br/Pesquisa?pagina={x+1}"
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
            value1 = values_div[0].find("ol").find("li", class_="fs-px-12").text.split()[1]
            value2 = values_div[1].find("ol").find("li", class_="fs-px-12").text.split()[1]
            value = min(value1, value2)
        else:
            value = values_div.find("ol").find("li", class_="fs-px-12").text.split()[1]

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
            appraisal_value = card.find("div", class_="col-md-4 order-0 order-md-1").find("div", class_="border-alt rounded p-4").find("span", style="text-decoration: line-through;").text.split("$")[1].lstrip().rstrip()
        except:  # noqa: E722
            try:
                appraisal_value = card.find("div", class_="col-md-4 order-0 order-md-1").find("div", class_="border-alt rounded p-4").find("span", style="text-decoration: none;").text.split("$")[1].lstrip().rstrip()
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
    soup = get_requests("https://www.megaleiloes.com.br/Pesquisa?tov=igbr&valor_max=10000000000&tipo%5B0%5D=1&tipo%5B1%5D=2&pagina=1")
    number_pages = int(soup.find("li", class_="last").find("a").get("data-page"))+1

    cards = []
    for x in range(number_pages):
        link = f"https://www.megaleiloes.com.br/Pesquisa?tov=igbr&valor_max=10000000000&tipo%5B0%5D=1&tipo%5B1%5D=2&pagina={x+1}"
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
            value1 = infos[1].find("span", class_="card-instance-value").text.split("$")[1].lstrip().rstrip()
            value2 = infos[2].find("span", class_="card-instance-value").text.split("$")[1].lstrip().rstrip()
            value = min(value1, value2)
        else:
            value = infos[1].find("span", class_="card-instance-value").text.split("$")[1].lstrip().rstrip()
    
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
        appraisal_value = soup.find("div", class_="rating-value").find("div", class_="value").text.split("$")[1].split("(")[0].lstrip().rstrip()

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
    urls = ["https://www.vivaleiloes.com.br/busca/#Engine=Start&Pagina=1&OrientacaoBusca=0&Busca=&Mapa=&ID_Categoria=0&ID_Estado=0&ID_Cidade=0&Bairro=&ID_Regiao=0&ValorMinSelecionado=0&ValorMaxSelecionado=0&Ordem=0&QtdPorPagina=9999999&ID_Leiloes_Status=1,3&SubStatus=&PaginaIndex=2&BuscaProcesso=&NomesPartes=&CodLeilao=&TiposLeiloes=[%22Judicial%22]&CFGs=[]", "https://www.vivaleiloes.com.br/busca/#Engine=Start&Pagina=1&OrientacaoBusca=0&Busca=&Mapa=&ID_Categoria=0&ID_Estado=0&ID_Cidade=0&Bairro=&ID_Regiao=0&ValorMinSelecionado=0&ValorMaxSelecionado=0&Ordem=0&QtdPorPagina=9999999&ID_Leiloes_Status=1,3&SubStatus=&PaginaIndex=1&BuscaProcesso=&NomesPartes=&CodLeilao=&TiposLeiloes=[%22Extrajudicial%22]&CFGs=[]"]

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

        appraisal_value = card.find("div", class_="dg-leiloes-valor-avaliacao").find("strong").text.split("$")[1].lstrip().split()[0]

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
            value1 = values.find("div").text.split("$")[1].replace("\n", "")
            value2 = values.find("span", class_="price-line-2-pracas").text.split("$")[1].replace("\n", "")
            value = min(value1, value2)
        except:
            value = values.find("span", class_="price-line").text.split("$")[1].replace("\n", "")
        
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
        img_cover = card.find("div", class_="carousel-item active h-100").find("img", class_="card-bem-img h-100").get("src")
        value = card.find("div", class_="bem-info").find("p", class_="float-right").text.split("$")[1].lstrip().rstrip()

        soup = get_requests(link)

        address = soup.find("div", class_="col-12 col-sm-8 col-md-9 my-1 mt-md-4 mt-xl-2").find_all("div", class_="col-12")[-1].text.split(":")[1].lstrip().rstrip()

        appraisal_value = soup.find("div", class_="col-12 col-md-10 col-lg-6 mb-3 pl-lg-5").find("p", class_="mb-0 destaque").text.split(":")[1].lstrip().rstrip()

        try:
            descricao = soup.find("div", class_="col-8 py-3").find("p").find("p").text
            areas = get_areas(descricao)

            area_util = areas[0]
            area_total = areas[1]
        except:
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
    soup = get_requests("https://www.grandesleiloes.com.br/")
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
        except:
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
        except:
            address = None

        appraisal_value = soup.find_all("div", class_="card-body")[-2].find("h4").text.split("$")[1].lstrip().rstrip()

        value = soup.find("p", class_="lance-inicial-valor").text.split("$")[1].lstrip().rstrip()


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
    urls = ["https://www.lancecertoleiloes.com.br/filtro/carros", "https://www.lancecertoleiloes.com.br/filtro/motos", "https://www.lancecertoleiloes.com.br/filtro/pesados", "https://www.lancecertoleiloes.com.br/filtro/outros", "https://www.lancecertoleiloes.com.br/filtro/imoveis"]
    cards = []
    for url in urls:
        soup = get_requests(url)
        numero_paginas = 1
        try:
            numero_paginas = int(soup.find("ul", id="ContentPlaceHolder1_rl_leilao_pagination").find_all("li")[-2].text)
        except:
            numero_paginas = 1

        for page in range(numero_paginas):
            soup = get_requests(f"{url}?pag={page}")
            cards_page = soup.find_all("div", class_="col-md-3 btn-leilao")
            for card in cards_page:
                cards.append(card)
            break#retirar

    data = []
    for card in cards:
        name = card.find("div", class_="lote-detalhes").find("div", class_="lote-descricao").text.lstrip().rstrip()
        link = f"https://www.lancecertoleiloes.com.br{card.find("a").get("href").replace("..", "")}"
        img_cover = card.find("img", class_="lote-img").get("src")
        
        soup = get_requests(link)
        value = soup.find("span", id="ContentPlaceHolder1_lblLanceinicial").text.split()[0]
        

        





        
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
        break
    return data

#mullerleiloes()
#lancese()
#francoleiloes()
#leilaosantos()
#leiloeirobonatto()
#lessaleiloes()
#rymerleiloes()
#grupolance()
#megaleiloes()
#vivaleiloes()
#biasileiloes()
#sanchesleiloes()
#grandesleiloes()
lancecertoleiloes()