# web-scraper-uber-trips

README - Criação e Uso do Executável

Este projeto realiza o scraping de dados e o pré-processamento das informações coletadas. O objetivo é extrair dados de relatórios, processá-los e salvá-los em arquivos CSV. O projeto utiliza Selenium para scraping e Pandas para manipulação de dados. Este README fornece instruções sobre como configurar o ambiente, instalar as dependências, criar o executável e executar o projeto.

Pré-requisitos

    Python 3.8 ou superior

Configuração do Ambiente
1. Clonar o Repositório

Clone o repositório para sua máquina local:

git clone https://github.com/felipeninek/web-scraper-uber-trips
dir web-scraper-uber-trips

2. Criar e Ativar a Virtual Environment

python -m venv venv
.\venv\Scripts\activate

3. Instalar as Dependências

pip install -r requirements.txt

4. Criar o Executável

pyinstaller --onefile main.py

5. Encontrar o Executável

Após a execução do PyInstaller, o executável será gerado no diretório dist. O caminho para o executável será:

dist/main.exe