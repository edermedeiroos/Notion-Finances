import requests
import json
import pandas
import openpyxl

with open("config.json", "r") as archive:
    configJson = json.load(archive)

# Acess Credential
SECRET = configJson["Internal Integration Secret"]
DATA_SOURCE_ID = configJson["Data Source ID"]
AUTH_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SECRET}",
    "Notion-Version": "2025-09-03"
}

urlDataSourceQuery = f"https://api.notion.com/v1/data_sources/{DATA_SOURCE_ID}/query"
bodyDataSourceQuery = {"sorts": [
        {
            "property": "Data",
            "direction": "ascending"
        },
        {   
            "property": "Transações",
            "direction": "ascending"
        },
        {   
            "property": "Valor",
            "direction": "ascending"
        }]
    }

# DataSource Request
dscRequest = requests.post(url=urlDataSourceQuery, 
                           json=bodyDataSourceQuery,
                           headers=AUTH_HEADERS
                           )
dscJson = dscRequest.json()

# DataFrame Data
generalData = []
dataColumns = ["ID", "Nome", "Valor", "Tipo", "Categoria", "Data", "Valor Efetivo", "Conta"]

# Primary Key Declaration
index = 1

# Iteraction over the pages from the list
while True:
    for object in dscJson["results"]:
        properties = object["properties"]

        # Object properties
        id = index
        name = properties["Transações"]["title"][0]["plain_text"]
        value = properties["Valor"]["number"]
        type = properties["Tipo"]["select"]["name"]
        category = properties["Categoria"]["select"]["name"]
        date = properties["Data"]["date"]["start"]
        efectiveValue = properties["Valor Efetivo"]["formula"]["number"]
        bankAccount = properties["Conta"]["select"]["name"]

        objectData = (id, name, value, type, category, date, efectiveValue, bankAccount)

        # Append to dataFrame
        generalData.append(objectData)

        # Primary Key
        index += 1

    # Verify if has more data
    if dscJson["has_more"]:
        # Cursor update for next page
        next_cursor = dscJson["next_cursor"]
        bodyDataSourceQuery["start_cursor"] = next_cursor

        dscRequest = requests.post(url=urlDataSourceQuery, 
                            json=bodyDataSourceQuery,
                            headers=AUTH_HEADERS
                            )
        dscJson = dscRequest.json()
    
    else:
        break

df = pandas.DataFrame(generalData, columns=dataColumns)

# Exportation
df.to_excel("Finanças.xlsx", index=False)
df.to_csv("FAT_TABLE.csv", index=False)
