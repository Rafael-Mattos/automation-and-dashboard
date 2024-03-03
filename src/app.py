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
import schedule
import streamlit as st

class App:
    def __init__(self, intervalo_dias_relatorio=365):
        """Cria a classe App. No momento da criação, pode ser passado o intervalo de dias que o relatório é gerado. Caso não informado, será adotado um período de 365 dias para as estatísticas."""

        # Configurações
        self.dif_dias = intervalo_dias_relatorio # Intervalo de dias a ser utilizado para gerar o relatório
        self.pasta_download = '/home/rafa/Downloads' # Local onde o arquivo é baixado
        self.numero = 0
    
    def trigger(self):

        # Configurações do Streamlit
        st.set_page_config(
            page_title="Estatísticas Chamados",
            page_icon=":chart_with_upwards_trend:",
            layout="wide",  # Define o layout para ocupar a largura total
            initial_sidebar_state="expanded",  # Expande a barra lateral inicialmente
        )

        # Centralizando as métricas e ocultando o cabeçalho
        st.markdown('''
            <style>
                header[data-testid="stHeader"] {
                    display: none;
                }
                
                div.st-emotion-cache-0:nth-child(2) {
                    margin-top: 0px;
                }
                    
                div.st-emotion-cache-ocqkz7:nth-child(1) > div:nth-child(1) > div:nth-child(1){
                    margin-top: 50px;
                }
                    
                [data-testid="stAppViewBlockContainer"] {
                    padding-top: 0px;
                }
                
                
                [data-testid="stMetric"] {
                    justify-content: center;
                    text-align: center;
                }

                [data-testid="stMetricLabel"] {
                    display: flex;
                    flex-direction:column; 
                    justify-content:center";
                }
            </style>
            ''', 
        unsafe_allow_html=True)

        self.container = st.empty()

        # Roda o script pela primeira vez
        self.main()

        # Agendamento da tarefa de atualização a cada minuto
        schedule.every(1).minutes.do(self.main)

        # Loop principal
        while True:
            schedule.run_pending()
            time.sleep(1)

    def main(self):
        
        # Carrega as variáveis de ambiente do arquivo .env
        load_dotenv()

        # Instanciando o Webdriver
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')

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

        # Atualizando informações
        with self.container.container():
            # Criando as duas colunas da primeira linha
            l1c1, l1c2 = st.columns(2)

            # Preenchendo a primeiro coluna da primeira linha
            l1c1.metric(
                label="Chamados em aberto",
                value=round(total_chamados),
            )
            l1c1.metric(
                label="Concluídos Hoje",
                value=round(concluidos_hoje),
            )

            # Gerando o gráfico por tipo de chamado e preenchendo segunda coluna da primeira linha
            grafico_tipos_chamados = self.gerar_grafico_tipos_chamados(df_tipos_chamados)
            l1c2.plotly_chart(grafico_tipos_chamados, use_container_width=True)

            # Criando as duas colunas da segunda linha
            l2c1, l2c2 = st.columns(2)

            # gerando gráfico por status dos chamados e preenchendo a primeira coluna da segunda linha
            grafico_status_chamados = self.gerar_grafico_status_chamados(df_status)
            l2c1.plotly_chart(grafico_status_chamados, use_container_width=True)

            # Gerando gráfico por chamados vencidos e preenchendo a segunda coluna da segunda linha
            grafico_vencidos = self.gerar_grafico_vencidos(df_vencidos)
            l2c2.plotly_chart(grafico_vencidos, use_container_width=True)

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
        df['descricao'] = df['descricao'].astype(str)
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

        df['intervalos_vencimentos'] = df['dias_ate_vencimento'].apply(self.separar_semanas)

        df_vencidos = df['intervalos_vencimentos'].value_counts().reset_index()
        df_vencidos.columns = ['vencidos', 'qtd']

        return df_vencidos.sort_values(by='qtd', ascending=True)
    
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
        
        return retorno
        

    #############################################################################################
    ### Métodos - Gráficos ######################################################################
    #############################################################################################
    
    def personaliza_graficos(self, grafico):
        """Estilo padrão para os gráficos a serem exibidos."""

        grafico.update_layout(
            paper_bgcolor='rgba(255,255,255,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            template="plotly_dark",  # Pode escolher um template pré-definido (exemplo: "plotly_dark")
            font=dict(family="Roboto", color="black"),  # Personalizar a fonte do texto
            title_x=0.5,
            title_font=dict(size=15, family='Roboto'),
            width=500,
            height=300,
            margin=dict(t=20)
        )

        # Atualizar barras para a cor específica (#011E4B)
        grafico.update_traces(
            marker_color='#011E4B',
            textposition='inside',
            textfont=dict(family='Roboto', size=12),
        )

        # Remover linhas verticais (grades) e legenda do eixo X
        grafico.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=False, showticklabels=False)
        grafico.update_yaxes(title_text='', showgrid=False, tickfont=dict(size=12))

        return grafico
    
    def gerar_grafico_tipos_chamados(self, df_descricao):
        """Gera o gráfico por tipo de chamados."""

        # Preenche as informações do gráfico
        fig = px.bar(
            df_descricao,
            x='qtd',
            y='descricao',
            orientation='h',
            title='Chamados por Descrição',
            labels={'qtd': 'Número de Ocorrências',
                    'descricao': 'Descrição'}
            )


        # Adicionando as etiquetas
        fig.update_traces(text=df_descricao['qtd'])

        # Aplicando personalização ao gráfico
        fig = self.personaliza_graficos(fig)

        return fig
    
    def gerar_grafico_status_chamados(self, df_situacao):
        """Gera um gráfico por status dos chamados que não estejam concluídos."""

        # Preenche as informações do gráfico
        fig = px.bar(
            df_situacao,
            x='qtd',
            y='situacao',
            orientation='h',
            title='Situação dos chamados',
            labels={'qtd': 'Número de Ocorrências',
                    'situacao': 'Situação'}
            )


        # Adicionando as etiquetas
        fig.update_traces(text=df_situacao['qtd'])

        # Aplicando personalização ao gráfico
        fig = self.personaliza_graficos(fig)

        return fig
    
    def gerar_grafico_vencidos(self, df_vencidos):
        """Gera um gráfico por status dos chamados que não estejam concluídos."""

        # Preenche as informações do gráfico
        fig = px.bar(
            df_vencidos,
            x='qtd',
            y='vencidos',
            orientation='h',
            title='Chamados Vencidos',
            labels={'qtd': 'Número de Ocorrências',
                    'vencidos': 'Vencimentos'}
        )


        # Adicionando as etiquetas
        fig.update_traces(text=df_vencidos['qtd'])

        # Aplicando personalização ao gráfico
        fig = self.personaliza_graficos(fig)

        return fig
    

if __name__ == '__main__':
    exec = App()
    exec.trigger()
