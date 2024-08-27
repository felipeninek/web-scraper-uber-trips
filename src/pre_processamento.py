import pandas as pd
from geopy.geocoders import Nominatim

def carregar_dados(caminho_arquivo):
    df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8')
    print(f"Dados carregados com sucesso. {len(df)} registros encontrados.")
    return df

def limpar_dados(df):
    df_limpo = df.dropna().drop_duplicates()
    print(f"Dados limpos. {len(df_limpo)} registros restantes após a limpeza.")
    return df_limpo

def converter_colunas(df):
    # Separando a coluna 'DataHora'
    df[['Categoria', 'Data', 'Hora']] = df['DataHora'].str.split(' • ', expand=True)

    meses_portugues_para_ingles = {
        'jan': 'Jan',
        'fev': 'Feb',
        'mar': 'Mar',
        'abr': 'Apr',
        'mai': 'May',
        'jun': 'Jun',
        'jul': 'Jul',
        'ago': 'Aug',
        'set': 'Sep',
        'out': 'Oct',
        'nov': 'Nov',
        'dez': 'Dec'
    }

    # Substituindo os meses em português pelos equivalentes em inglês
    df['Data'] = df['Data'].replace(meses_portugues_para_ingles, regex=True)

    # Convertendo a coluna 'Data' para o formato datetime
    df['Data'] = pd.to_datetime(df['Data'], format='%d de %b. de %Y', dayfirst=True)

    # Unindo a coluna 'Data' com a coluna 'Hora'
    df['DataHora'] = pd.to_datetime(df['Data'].astype(str) + ' ' + df['Hora'])

    # Removendo o símbolo de moeda, substituindo vírgula por ponto e convertendo para float
    df['Preco'] = df['Preco'].str.replace('R\$', '', regex=True).str.replace('.', '').str.replace(',', '.').astype(float)

    # Função para converter a duração em minutos inteiros
    def converter_para_minutos(duracao):
        partes = duracao.split(' ')
        minutos = int(partes[0])
        segundos = 0
        minutos_totais = minutos + segundos // 60
        return minutos_totais

    # Aplicando a função à coluna 'Duracao'
    df['Duracao'] = df['Duracao'].apply(converter_para_minutos)

    # Converter Distancia para float
    def converter_para_km(distancia):
        distancia = distancia.split(' ')
        km = distancia[0].replace(',', '.')
        return float(km)

    df['Distancia'] = df['Distancia'].apply(converter_para_km)

    # Funções para separar origem e destino
    def extrair_dados_endereco(localizacao):
        try:
            partes = localizacao.split(' - ')
            rua, cidade_cep = partes[0].split(', ')
            cidade = partes[1]
            cep = partes[2].split(', ')[1]
            return rua, cidade, cep
        except (IndexError, ValueError):
            return None, None, None

    df[['RuaOrigem', 'CidadeOrigem', 'CEPOrigem']] = df['Origem'].apply(extrair_dados_endereco).apply(pd.Series)
    df[['RuaDestino', 'CidadeDestino', 'CEPDestino']] = df['Destino'].apply(extrair_dados_endereco).apply(pd.Series)

    # Convertendo a coluna 'DataHora' para datetime
    df['DataHora'] = pd.to_datetime(df['DataHora'])

    # Inicializar o geocodificador
    geolocator = Nominatim(user_agent="app")

    def geocode_address(endereco):
        try:
            location = geolocator.geocode(endereco)
            if location:
                return location.latitude, location.longitude
            else:
                return None, None
        except Exception as e:
            print(f"Erro ao geocodificar o endereço {endereco}: {e}")
            return None, None

    # Aplicar geocodificação para os endereços de origem e destino no DataFrame
    df['LatOrigem'], df['LonOrigem'] = zip(*df.apply(lambda row: geocode_address(f"{row['RuaOrigem']}, São Paulo, Brasil"), axis=1))
    df['LatDestino'], df['LonDestino'] = zip(*df.apply(lambda row: geocode_address(f"{row['RuaDestino']}, São Paulo, Brasil"), axis=1))

    # Adicionar colunas para dia da semana, semana do mês e mês do ano
    df['DiaSemana'] = df['DataHora'].dt.day_name()
    df['SemanaMes'] = df['DataHora'].dt.day // 7 + 1  # Calcula a semana do mês (1-4)
    df['MesAno'] = df['DataHora'].dt.month

    # Dropar colunas desnecessárias
    df = df.drop(columns=['Data', 'Hora', 'Origem', 'Destino', 'url'])

    # Limpar inconsistências resultantes da consulta na API
    df = limpar_dados(df)

    return df

def salvar_dados_processados(df, caminho_arquivo):
    df.to_csv(caminho_arquivo, sep=';', encoding='utf-8', index=False)
    print(f"Dados processados salvos em {caminho_arquivo}")
