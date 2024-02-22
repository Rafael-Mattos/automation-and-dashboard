import os
import sys
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import pandas as pd
from glob import glob
import plotly.express as px
import time

class App:
    def __init__(self, intervalo_dias_relatorio=365):

        # Configurações
        self.dif_dias = intervalo_dias_relatorio # Intervalo de dias a ser utilizado para gerar o relatório
        self.pasta_download = '/home/rafa/Downloads' # Local onde o arquivo é baixado

    def main(self):

        # Carrega as variáveis de ambiente do arquivo .env
        load_dotenv()

        # Instanciando o Webdriver
        options = webdriver.FirefoxOptions()
        self.driver = webdriver.Firefox(options=options)

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

        # Um vez baixado o arquivo, cria-se o df e em seguida o arquivo será excluído
        self.criar_df()

        # Limpeza dos dados
        self.limpar_dados()

        # Criar df apenas para chamados não concluídos
        self.criar_df_chamados_em_aberto()

        # Obtendo os dados a serem exibidos
        total_chamados = self.calcular_total_chamados()

        concluidos_hoje = self.calcular_concluidos_hoje()

        df_tipos_chamados = self.gerar_df_tipos_chamados()

        df_status = self.gerar_df_status_chamados()

        df_vencidos = self.gerar_df_vencidos()

        print('Total de chamados:', total_chamados)
        print('##############################################')
        print('##############################################')
        print('Concluídos hoje:', concluidos_hoje)
        print('##############################################')
        print('##############################################')
        print('DF - Tipos chamados:', df_tipos_chamados)
        print('##############################################')
        print('##############################################')
        print('DF - Status:', df_status)
        print('##############################################')
        print('##############################################')
        print('DF - Status:', df_vencidos)
        print('##############################################')
        print('##############################################')
        
    

    #############################################################################################
    ### Métodos - Automações ####################################################################
    #############################################################################################

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
    
    #############################################################################################
    ### Métodos - Carregamento e limpeza dos dados ##############################################
    #############################################################################################

    def criar_df(self):
        """Busca o arquivo baixado e o transforma em um dataframe."""

        # Caso a pasta configurada não esteja terminada em "/", concatena uma "/" ao final do caminho
        if self.pasta_download[-1] != '/':
            self.pasta_download += '/'
        
        # Encontrando o arquivo baixado
        tentativa = 0

        while tentativa <= 5:
            # Faz algumas tentativas de encontrar o arquivo baixado, pois em alguns casos pode haver demora para baixar o relatório
            arqs = glob(f'{self.pasta_download}relatorio_*.csv')

            # Se encontrar algum arquivo, sai do loop
            if len(arqs) > 0:
                break
            
            # Se nao encontrar o arquivo, aguarda 5 segundos e tenta encontrar o arquivo novamente
            # Isso é necessário considerando que o arquivo pode demorar um pouco para ser baixado
            time.sleep(5)
            tentativa += 1
        
        # Criando o dataframe
        try:
            self.df = pd.read_csv(arqs[-1])

        except Exception as e:
            # Esta exceção irá encerrar a execução do programa, pois, mesmo após todas as tentativas, não foi baixado nenhum relatório
            print('Verifique  o erro:', str(e))
            sys.exit()
        
        # Excluindo arquivo do relatório baixado
        try:
            # Se, por algum motivo, houver mais de um relatório na pasta, já exclui todos, pois isso iria gerar um erro nas estatísticas da próxima vez que o código rodasse
            for arq in arqs:
                os.remove(arq)
        
        except Exception as e:
            print('Relatório não foi excluído, verificar o erro:', e)


    def limpar_dados(self):
        """Limpa e formata os dados para que os mesmos possam ser analisados posteriormente."""

        # Renomeando as colunas
        self.df = self.df.rename(columns={
            'Aberto Em': 'abertura',
            'Solicitação': 'descricao',
            'Situação': 'situacao',
            'Vencimento': 'vencimento',
            'Concluído Em': 'conclusao'
        })

        # Convertendo colunas "abertura", "vencimento" e "conclusao" para o tipo data
        self.df['abertura'] = pd.to_datetime(self.df['abertura'], format='%d.%m.%Y')
        self.df['vencimento'] = pd.to_datetime(self.df['vencimento'], format='%d.%m.%Y')
        self.df['conclusao'] = pd.to_datetime(self.df['conclusao'], format='%d.%m.%Y', errors='coerce')

        # Convertendo colunas "descricao" e "situacao" para o tipo categoria
        self.df['descricao'] = self.df['descricao'].astype('category')
        self.df['situacao'] = self.df['situacao'].astype('category')

        # Transformando a coluna 'Cod' no índice do DataFrame
        self.df = self.df.set_index('Cod')
    
    def criar_df_chamados_em_aberto(self):
        """Cria um df apenas para os chamados em aberto."""

        # Faz uma cópia do df completo
        self.df_nao_concluidos = self.df.copy()

        # Filtrando apenas as linhas não concluídas
        self.df_nao_concluidos = self.df_nao_concluidos.loc[self.df_nao_concluidos['situacao'] != 'Concluído']
        
        # Excluindo a coluna de data da conclusão, já que ela ficará vazia
        self.df_nao_concluidos = self.df_nao_concluidos.drop('conclusao', axis=1)

        # Criando a coluna para os dias até o vencimento do chamado
        data_atual = pd.to_datetime(datetime.now().date())
        self.df_nao_concluidos['dias_ate_vencimento'] = (self.df_nao_concluidos['vencimento'] - data_atual).dt.days
    

    #############################################################################################
    ### Métodos - Análise dos dados #############################################################
    #############################################################################################

    def calcular_total_chamados(self):
        """Retorna o número total de chamados que não estejam concluídos."""

        return len(self.df_nao_concluidos)

    def calcular_concluidos_hoje(self):
        """Retorna o número total de chamados concluídos no dia."""

        data_atual = datetime.now().date()
        return len(self.df[self.df['conclusao'].dt.date == data_atual])
    
    def gerar_df_tipos_chamados(self):
        """Gera o df com a quantidade de cada tipo de chamado. Considera apenas chamados não concluídos."""

        df = self.df_nao_concluidos.copy()

        df_descricao = df['descricao'].value_counts().reset_index()
        df_descricao.columns = ['descricao', 'qtd']
        df_descricao = df_descricao.sort_values(by='qtd', ascending=True)

        return df_descricao
    
    def gerar_df_status_chamados(self):
        """Gera o df com a quantidade de chamados por status. Considera apenas chamados não concluídos."""

        df = self.df_nao_concluidos.copy()

        df['situacao'] = df['situacao'].astype('object') # Se mantivesse como "category", apareceria uma linha nas estatísticas para o valor "Concluído", mesmo que ele estivesse zerado
        df_situacao = df['situacao'].value_counts().reset_index()
        df_situacao.columns = ['situacao', 'qtd']
        df_situacao = df_situacao.sort_values(by='qtd', ascending=True)

        return df_situacao
    
    def gerar_df_vencidos(self):
        """Gera df contendo os chamados vencidos, separados em grupos de acordo com um intervalo de dias fornecido."""
        
        df = self.df_nao_concluidos.copy()

        # df['intervalos_vencimentos'] = df['dias_ate_vencimento'] // 7
        df['intervalos_vencimentos'] = df['dias_ate_vencimento'].apply(self.separar_semanas)

        return df
    
    def separar_semanas(self, dias_vencimento):
        """Cria a legenda para o dataframe df_vencidos."""

        semanas_vencimento = int(dias_vencimento / 7)

        # return semanas_vencimento

        if dias_vencimento == 0: #Está na semana do vencimento
            retorno = 'Vence em até uma semana'
        elif semanas_vencimento > 0:
            retorno = f'Vencerá entre {semanas_vencimento} e {semanas_vencimento + 1}'
        elif semanas_vencimento < 0:
            retorno = f'Vencido há mais de {abs(semanas_vencimento)}'
        
        match dias_vencimento:
            case 0:
                retorno = 'Vence hoje'
            case _ if dias_vencimento > 0 and semanas_vencimento == 0:
                retorno = 'Vence em até uma semana'
            case _ if semanas_vencimento > 0:
                retorno = f'Vencerá entre {semanas_vencimento} e {semanas_vencimento + 1} semana(s)'
            case _ if dias_vencimento < 0 and semanas_vencimento == 0:
                retorno = 'Vencido há menos de uma semana'
            case _ if semanas_vencimento < 0:
                retorno = f'Vencido há mais de {abs(semanas_vencimento)} semana(s)'
            # case _: # Esse seria o "else"
            #     print("O número não se encaixa nos casos anteriores")
        
        return retorno

        #if dias_ate_vencimento > 0:


    #############################################################################################
    ### DEBUG ###################################################################################
    #############################################################################################

    def testes(self):
        print('Resultado:', int(1.999))

if __name__ == '__main__':
    exec = App()
    exec.main()
    # exec.testes()


