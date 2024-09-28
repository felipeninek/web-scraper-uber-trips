import os
import time
import pandas as pd
import PyPDF2
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def criar_pasta(caminho_pasta):
    if not os.path.exists(caminho_pasta):
        os.makedirs(caminho_pasta)
    return caminho_pasta

def criar_pasta_dados():
    return criar_pasta(os.path.join(os.getcwd(), "dados"))

def criar_pasta_output():
    return criar_pasta('output')

def configurar_driver(pasta_dados):
    preferencias = {
        'download.default_directory': pasta_dados,
        'profile.default_content_setting_values.automatic_downloads': 1
    }

    opcoes = Options()
    opcoes.add_argument('start-maximized')
    opcoes.add_argument('--disable-notifications')
    opcoes.add_argument('--no-sandbox')
    opcoes.add_argument('--verbose')
    opcoes.add_experimental_option('prefs', preferencias)

    servico = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=servico, options=opcoes)

def verificar_login(driver):
    driver.get('https://drivers.uber.com/p3/payments/statements')
    espera = WebDriverWait(driver, 10)
    login_efetuado = False

    while not login_efetuado:
        try:
            espera.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[1]/div/div[2]/div/h5')))
            login_efetuado = True
        except Exception:
            pass

def baixar_arquivos(driver):
    espera = WebDriverWait(driver, 30)
    mes = date.today().month
    ano = date.today().year
    driver.get(f'https://drivers.uber.com/earnings/statements?month={mes}&year={ano}')
    
    espera.until(EC.presence_of_all_elements_located((By.CLASS_NAME, '_css-drSZEJ')))
    n_links = int(len(driver.find_elements(By.CLASS_NAME, '_css-drSZEJ')) / 2)

    if n_links == 0:
        if mes == 1:
            mes = 12
            ano -= 1
        else:
            mes -= 1
        driver.get(f'https://drivers.uber.com/earnings/statements?month={mes}&year={ano}')

    continuar = True

    while continuar:
        try:
            espera.until(EC.presence_of_all_elements_located((By.CLASS_NAME, '_css-drSZEJ')))
            n_links = int(len(driver.find_elements(By.CLASS_NAME, '_css-drSZEJ')) / 2)
            
            if n_links > 0:
                for link in range(1, n_links + 1):
                    print(f'Baixando PDF | Ano: {ano} | Mês: {mes} | Semana: {link}/{n_links}')
                    download_pdf = espera.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="wrapper"]/div[2]/div/div[2]/div[1]/div/table/tbody/tr[{link}]/td[4]/button')))
                    download_pdf.click()
           
                if mes == 1:
                    mes = 12
                    ano -= 1
                else:
                    mes -= 1
                
                time.sleep(10)
                driver.get(f'https://drivers.uber.com/earnings/statements?month={mes}&year={ano}')
            else:
                continuar = False
        except Exception as e:
            print(f'Erro ao processar página: {e}')
            continuar = False

def extrair_links(caminho_pdf):
    lista_links = []
    for root, subpastas, arquivos in os.walk(caminho_pdf):
        for arquivo in arquivos:
            caminho_arquivo = os.path.join(root, arquivo)
            with open(caminho_arquivo, 'rb') as pdf_file:
                pdf = PyPDF2.PdfReader(pdf_file)
                paginas = len(pdf.pages)
                chave = '/Annots'
                uri = '/URI'
                acao = '/A'

                for pagina in range(paginas):
                    print(f"Página atual: {pagina + 1}")
                    pagina_recortada = pdf.pages[pagina]
                    objeto_pagina = pagina_recortada.get_object()
                    if chave in objeto_pagina.keys():
                        anotacoes = objeto_pagina[chave]
                        for anotacao in anotacoes:
                            u = anotacao.get_object()
                            if uri in u[acao].keys():
                                lista_links.append(u[acao][uri])
                        
    return lista_links

def fazer_scraping_viagens(driver, lista_links):
    df = pd.DataFrame(columns=[
        'DataHora',
        'Preco',
        'Duracao',
        'Distancia',
        'Origem',
        'Destino',
        'url'
    ])

    print('DataFrame criado')
    lista_erros = []

    for link in lista_links:
        try:
            driver.get(link)
            print(f'Iniciando scraping da viagem: {lista_links.index(link) + 1} / {len(lista_links)}')
            print('Objetos com erro:', len(lista_erros))
            time.sleep(2)

            DataHora = driver.find_element(By.XPATH, '//*[@id="wrapper"]/div/ol/li[1]/div[1]/p[1]').text
            Preco = driver.find_element(By.XPATH, '//*[@id="wrapper"]/div/ol/li[1]/div[1]/h2').text
            Duracao = driver.find_element(By.XPATH, '//*[@id="wrapper"]/div/ol/li[1]/div[3]/div[1]/div[2]').text
            Distancia = driver.find_element(By.XPATH, '//*[@id="wrapper"]/div/ol/li[1]/div[3]/div[2]/div[2]').text
            Origem = driver.find_element(By.XPATH, '//*[@id="wrapper"]/div/ol/li[1]/div[4]/div[1]/div[2]/div/p').text
            Destino = driver.find_element(By.XPATH, '//*[@id="wrapper"]/div/ol/li[1]/div[4]/div[2]/div[2]/div/p').text

            dados = pd.DataFrame({
                'DataHora': DataHora,
                'Preco': Preco,
                'Duracao': Duracao,
                'Distancia': Distancia,
                'Origem': Origem,
                'Destino': Destino,
                'url': link
            }, index=[0])
            print('Objeto criado')

            df = pd.concat([df, dados], ignore_index=True)
            print('Objeto adicionado ao DataFrame')
            print('')

        except Exception as e:
            print(f"Erro ao processar o link: {link}. Erro: {e}")
            lista_erros.append(link)

    return df, lista_erros

def salvar_dados(df, caminho_pasta='dados', nome_arquivo='corridas_extraidas.csv'):
    if not os.path.exists(caminho_pasta):
        os.makedirs(caminho_pasta)

    caminho_completo = os.path.join(caminho_pasta, nome_arquivo)
    df.to_csv(caminho_completo, sep=';', encoding='utf-8', index=False)
    print(f'Dados salvos com sucesso em: {caminho_completo}')
