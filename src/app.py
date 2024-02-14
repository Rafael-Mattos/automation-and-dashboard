import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By


# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()


# Obtém as credenciais do ambiente
login = os.getenv("LOGIN")
senha = os.getenv("SENHA")

# Configurando o Selenium
options = webdriver.FirefoxOptions()
driver = webdriver.Firefox(options=options)

# Acessando o sistema
link_sistema = 'http://localhost:8080'
driver.get(link_sistema)

# Digitar dados de login e acessar sistema
driver.find_element(By.XPATH, '//*[@id="email"]').clear()
driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(login)
driver.find_element(By.XPATH, '//*[@id="password"]').clear()
driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(senha)
driver.find_element(By.XPATH, '//*[@id="login-button"]').click()

"""
Testes:



"""


