import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import pandas as pd
from glob import glob
import plotly.express as px

class App:
    def __init__(self, intervalo_dias_relatorio=365):
        # Instanciando o Webdriver
        options = webdriver.FirefoxOptions()
        self.driver = webdriver.Firefox(options=options)
        self.dif_dias = intervalo_dias_relatorio

    def main(self):

        # Carrega as variáveis de ambiente do arquivo .env
        load_dotenv()

        # Obtém as credenciais do ambiente
        login = os.getenv("LOGIN")
        senha = os.getenv("SENHA")

        # Acessando o sistema
        link_sistema = 'http://localhost:8080'
        self.driver.get(link_sistema)
        
        ### Fazendo login no sistema ############################################################
        self.preenche_input('//*[@id="email"]', login)
        self.preenche_input('//*[@id="password"]', senha)
        self.driver.find_element(By.XPATH, '//*[@id="login-button"]').click()

        ### Preencher informações e baixar relatório ############################################

        # Configurando as datas de início e de fim (estão no formato aaaa-mm-dd porque o tipo do input é "date")
        data_final = datetime.now().date()
        data_final_formatada = data_final.strftime("%Y-%m-%d") # Convertendo a data obtida para string
        
        data_inicio = data_final - timedelta(self.dif_dias)
        data_inicio_formatada = data_inicio.strftime("%Y-%m-%d") # Convertendo a data obtida para string

        # Preenchendo as datas
        self.preenche_input('//*[@id="data_inicio"]', data_inicio_formatada)
        self.preenche_input('//*[@id="data_fim"]', data_final_formatada)

        # Marcando os checkboxes
        self.marca_chackbox('//*[@id="pendente"]')
        self.marca_chackbox('//*[@id="finalizado"]')

        # Clicando no botão para baixar o relatório
        self.driver.find_element(By.XPATH, '/html/body/form/button').click()

        # Fecha o navegador
        self.driver.quit()
    
    def preenche_input(self, xpath, conteudo):
        """Limpa o conteúdo de um input e em seguida preenche seu conteúdo. Utiliza o XPATH para identificar o input a ser preenchido."""

        alvo = self.driver.find_element(By.XPATH, xpath)
        alvo.clear()
        alvo.send_keys(conteudo)
    
    def marca_chackbox(self, xpath):
        """Marca um determinado checkbox, caso o mesmo esteja desmarcado. Utiliza o XPATH para identificar o checkbox a ser marcado."""
        checkbox = self.driver.find_element(By.XPATH, xpath)
        
        if not checkbox.is_selected():
            checkbox.click()

if __name__ == '__main__':
    exec = App()
    exec.main()

"""
Testes:



"""


