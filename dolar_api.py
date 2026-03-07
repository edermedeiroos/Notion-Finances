import requests
import pandas as pd
from datetime import datetime

# ----------------------------------------------------------------------------
#                             DOLAR FEES - ETL
#
# 1) Request to Brazil Bank API
# 2) DIM table with dolar fees along time
# ----------------------------------------------------------------------------

data_inicio_cotacao = "01-01-2025"
data_fim_cotacao = datetime.today().strftime('%m-%d-%Y')

dolar_url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@dataInicial='{data_inicio_cotacao}'&@dataFinalCotacao='{data_fim_cotacao}'&$orderby=dataHoraCotacao%20desc&$format=json"

dolar_request = requests.get(url=dolar_url)
dolar_json = dolar_request.json()
dolar_data = []
dolar_columns = ["COTACAO_COMPRA", "COTACAO_VENDA", "DATA_HORA"]

for ct in dolar_json['value']: 
    cotacao_compra = ct.get("cotacaoCompra")
    cotacao_venda = ct.get("cotacaoVenda")
    data_hora = ct.get("dataHoraCotacao")
    dolar_data.append((cotacao_compra, cotacao_venda, data_hora))

df_dolar = pd.DataFrame(dolar_data, columns=dolar_columns)
print(df_dolar)