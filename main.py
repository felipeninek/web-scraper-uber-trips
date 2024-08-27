import os

# Importar as funções definidas
from src.web_scraping import criar_pasta_dados, criar_pasta_output, configurar_driver, verificar_login, baixar_arquivos, extrair_links, fazer_scraping_viagens, salvar_dados
from src.pre_processamento import carregar_dados, limpar_dados, converter_colunas, salvar_dados_processados

import warnings
warnings.filterwarnings('ignore')

def main():
    # 1. Criar pasta para armazenar os dados
    pasta_dados = criar_pasta_dados()

    # 2. Criar pasta 'output' para salvar os arquivos processados
    pasta_output = criar_pasta_output()

    # 3. Configurar o driver do Selenium
    driver = configurar_driver(pasta_dados)

    # 4. Verificar se o login foi efetuado
    verificar_login(driver)

    # 5. Baixar arquivos de relatórios
    baixar_arquivos(driver)

    # 6. Extrair os links dos PDFs baixados
    caminho_pdf = pasta_dados  # Ajuste para o caminho correto onde os PDFs são baixados
    lista_links = extrair_links(caminho_pdf)

    ##################### filtrar para teste ############################
    lista_links = lista_links[:500]

    # 7. Fazer scraping das informações das viagens
    df, lista_erros = fazer_scraping_viagens(driver, lista_links)

    # 8. Salvar os dados extraídos em um arquivo CSV
    caminho_csv_extraidos = os.path.join(pasta_output, 'corridas_extraidas.csv')
    salvar_dados(df, caminho_pasta=pasta_output, nome_arquivo='corridas_extraidas.csv')

    # Encerrar o driver
    driver.quit()

    # 9. Pré-processar os dados extraídos
    df = carregar_dados(caminho_csv_extraidos)
    df = limpar_dados(df)
    df = converter_colunas(df)
    caminho_csv_processados = os.path.join(pasta_output, 'corridas_processadas.csv')
    salvar_dados_processados(df, caminho_arquivo=caminho_csv_processados)

    # 10. Exibir mensagem final
    if lista_erros:
        print(f"Erro ao processar {len(lista_erros)} links. Verifique a lista de erros para mais detalhes.")
    else:
        print("Processo concluído com sucesso. Todos os links foram processados.")

if __name__ == '__main__':
    main()
