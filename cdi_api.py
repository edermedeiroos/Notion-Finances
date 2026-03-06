import requests
import json
import pandas as pd
import openpyxl
import sqlalchemy

# ----------------------------------------------------------------------------
#                             CDI FEES - ETL
#
# 1) Request to Brazil Bank API
# 2) DIM table with cdi fees along time
# ----------------------------------------------------------------------------

cdi_url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados"
cdi_params = {
    "formato": "json",
    "dataInicial": "01/01/2025"
}
cdi_request = requests.get(url=cdi_url, params=cdi_params)
cdi_json = cdi_request.json()
cdi_data = []
cdi_columns = ["DATA", "TAXA"]

for tx in cdi_json:
    date = tx.get("data")
    taxa = tx.get("valor")
    cdi_data.append((date, taxa))

df_cdi = pd.DataFrame(cdi_data, columns=cdi_columns)
