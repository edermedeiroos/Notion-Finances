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
dataColumns = ["ID", "NAME", "VALUE", "TYPE", "CATEGORY", "SUB_CATEGORY", "DATE", "EFECTIVE_VALUE", "ASSOCIATED", "ACCOUNT"]

# Primary Key Declaration
index = 1

# Iteraction over the pages from the list
while True:
    for object in dscJson["results"]:
        properties = object["properties"]

        id = index
        
        # 1. Name
        try:
            name = properties["Transações"]["title"][0]["plain_text"]
        except (KeyError, IndexError, TypeError):
            name = "Sem Título"

        # 2. Value
        try:
            value = properties["Valor"]["number"]
        except (KeyError, TypeError):
            value = 0.0

        # 3. Type
        try:
            type = properties["Tipo"]["select"]["name"]
        except (KeyError, TypeError):
            type = None

        # 4. Category
        try:
            category = properties["Categoria"]["select"]["name"]
        except (KeyError, TypeError):
            category = None

        # 5. Sub-Category
        try:
            subCategory = properties["Sub-Categoria"]["select"]["name"]
        except (KeyError, TypeError, AttributeError):
            subCategory = None

        # 6. Date
        try:
            date = properties["Data"]["date"]["start"]
        except (KeyError, TypeError):
            date = None

        # 7. Efective Value
        try:
            efectiveValue = properties["Valor Efetivo"]["formula"]["number"]
        except (KeyError, TypeError):
            efectiveValue = 0.0

        # 8. Associated People
        try:
            associated_list = [associated["name"] for associated in properties["Associado"]["multi_select"]]
            associated_people = ", ".join(associated_list)
        except (KeyError, TypeError):
            associated_people = None

        # 9. Account
        try:
            bankAccount = properties["Conta"]["select"]["name"]
        except (KeyError, TypeError):
            bankAccount = None

        objectData = (id, name, value, type, category, subCategory, date, efectiveValue, associated_people, bankAccount)

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
df.to_excel("C:\BI\FinancesDB\Finanças.xlsx", index=False)
df.to_csv("C:\BI\FinancesDB\FAT_TABLE.csv", index=False)
