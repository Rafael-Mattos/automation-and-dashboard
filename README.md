# Automação, análise de dados e montagem de dashboard com Python

## Sobre o projeto
É comum encontrar sistemas de abertura de chamados que funcionam no navegador, porém, que não possuem uma API específica para se realizar consultas sobre as informações dos chamados, tais sistemas apenas disponibilizam uma função para gerar relatórios em CSV ou XLSX. Para coletar informações de modo contínuo desse tipo de sistema, uma solução possível é a construção de um RPA, que faça toda a interação com o sistema até que seja gerado o relatório com as informações de chamado.

Esse projeto trabalhou com este tipo de solução e percorre as seguintes etapas:
- Inicia-se com uma automação que faz o login e gera um relatório em um sistema ilustrativo;
- Em seguida, realiza uma limpeza e análise dos dados dos chamados;
- Por fim, lança os dados obtidos em um dashboard construído através do Streamlit;

O processo se repete a cada determinado período de tempo, ou seja, o dashboard é dinâmico e se atualiza conforme configurado pelo usuário.

## O projeto está dividido em quatro seções principais
### Sistema de chamados
Trata-se de um sistema meramente ilustrativo, pois não é o foco do projeto. Possui uma tela de login simples na qual a validação ocorre pelo próprio JS da página. Após a etapa do login, ocorre o redirecionamento para um formulário, que simula algumas informações a serem preenchidas em um sistema para se gerar um relatório de chamados. Porém, por se tratar de um sistema ilustrativo, independente das informações preenchidas, o mesmo relatório será gerado. Trata-se de um arquivo CSV que se encontra na pasta "sistema_chamados/site/dados".

Após clicar para gerar o relatório, esse arquivo será baixado para a pasta de downloads e é este arquivo que será lido e em seguida apagado pela automação.

### Automação
Já no código python, foi utilizada a biblioteca Selenium para a interação com o sistema de chamados. Através da automação é que o script realiza o login, preenche as informações no formulário do sistema de chamados e baixa o relatório resultante da consulta. Tudo é feito por meio do Firefox que é executado de maneira oculta, ou seja, toda essa interação com o navegador não é visualizada, isso evita alternância entre janelas.

Essa automação está configurada para executar estas ações a cada um minuto, porém, ao colocar este sistema em produção, sugere-se aumentar este período para quinze minutos ou de acordo com a necessidade. A biblioteca utilizada para controlar este intervalo de tempo é a Schedule. Também cabe salientar que as informações utilizadas para o login no sistema se encontram no arquivo ".env".

### Análise dos dados
Após baixado o relatório, o script busca na pasta de downloads pelo relatório, converte ele para um dataframe do pandas e em seguida exclui o arquivo. Já a partir do dataframe Pandas, são realizadas as operações para limpeza dos dados e em seguida as operações necessárias para se extrair as informações necessárias para o dashboard. Estas informações já são organizadas de modo que fiquem prontas para serem exibidas no dashboard.

### Dashboard
Em posse das informações, foram utilizadas as bibliotecas Streamlit e Plotly para se criar o dashboard. Importante observar que o dashboard se atualiza automaticamente sempre que um novo relatório é baixado pela automação.

## Dashboard resultante
<img src="https://github.com/Rafael-Mattos/automation-and-dashboard/blob/main/tela_dashboard_sem_filtro.png">


# Autor
<span>Rafael Rosa de Mattos</span><br/><br/>
<a href="https://www.linkedin.com/in/rafael-rosa-de-mattos/" target="_blank"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a>
