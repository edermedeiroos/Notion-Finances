import requests
import json
import pandas
import openpyxl

with open("config.json", "r") as archive:
    configJson = json.load(archive)

# Acess Credential
SECRET = configJson["Internal Integratin Secret"]
AUTH_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SECRET}",
    "Notion-Version": "2025-09-03"
}

urlDataSourceQuery = "https://api.notion.com/v1/data_sources/25b22a3e-ef57-8147-ae65-000b8dd610e3/query"
bodyDataSourceQuery = {"sorts": [
        {
            "property": "Data",
            "direction": "descending"
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
dataColumns = ["Nome", "Valor", "Tipo", "Categoria", "Data", "Valor Efetivo"]

# Iteraction over the pages from the list
for object in dscJson["results"]:
    properties = object["properties"]

    # Object properties
    name = properties["Transações"]["title"][0]["plain_text"]
    value = properties["Valor"]["number"]
    type = properties["Tipo"]["select"]["name"]
    category = properties["Categoria"]["select"]["name"]
    date = properties["Data"]["date"]["start"]
    efectiveValue = properties["Valor Efetivo"]["formula"]["number"]

    objectData = (name, value, type, category, date, efectiveValue)

    # Append to dataFrame
    generalData.append(objectData)
    print(objectData)

df = pandas.DataFrame(generalData, columns=dataColumns)

print(df)
df.to_excel("Finanças.xlsx", index=False)
