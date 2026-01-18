import requests
import json
import pandas
import openpyxl
import sqlalchemy

with open("config.json", "r") as archive:
    configJson = json.load(archive)

# Acess Credential to DataBase + Engine
DB_USER = configJson.get("DB_USER")
DB_PASSWORD = configJson.get("DB_PASSWORD")
DB_HOST = configJson.get("DB_HOST")
DB_PORT = configJson.get("DB_PORT")
DB_DATABASE = configJson.get("DB_DATABASE")

engine = sqlalchemy.create_engine(
    f"mariadb+mysqldb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
)

# Acess Credential to API
SECRET = configJson["INTERNAL_INTEGRATION_SECRET"]
DATA_SOURCE_ID = configJson["DATA_SOURCE_ID"]
AUTH_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SECRET}",
    "Notion-Version": "2025-09-03"
}

urlDataSourceQuery = f"https://api.notion.com/v1/data_sources/{DATA_SOURCE_ID}/query"
bodyDataSourceQuery = {"sorts": [
        {
            "property": "Date",
            "direction": "ascending"
        },
        {   
            "property": "Name",
            "direction": "ascending"
        },
        {   
            "property": "Value",
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
dataColumns = ["ID", "NAME", "VALUE", "TYPE", "CATEGORY", "SUB_CATEGORY", "DATE", "EFECTIVE_VALUE", "ACCOUNT"]

# Primary Key Declaration
index = 1

# Iteraction over the pages from the list
while True:
    for item in dscJson["results"]:
        properties = item["properties"]
        
        # 1. Name
        try:
            name = properties["Name"]["title"][0]["plain_text"]
        except (KeyError, IndexError, TypeError):
            name = "Sem Título"

        # 2. Value
        try:
            value = round(float(properties["Value"]["number"]), 2)
        except (KeyError, TypeError):
            value = 0.0

        # 3. Type
        try:
            transaction_type = properties["Type"]["select"]["name"]
        except (KeyError, TypeError):
            transaction_type = None

        # 4. Category
        try:
            category = properties["Category"]["select"]["name"]
        except (KeyError, TypeError):
            category = None

        # 5. Sub-Category
        try:
            subCategory = properties["Sub Category"]["select"]["name"]
        except (KeyError, TypeError, AttributeError):
            subCategory = None

        # 6. Date
        try:
            date = properties["Date"]["date"]["start"]
        except (KeyError, TypeError):
            date = None

        # 7. Efective Value
        try:
            efectiveValue = properties["Effective Value"]["formula"]["number"]
        except (KeyError, TypeError):
            efectiveValue = 0.0

        # 8. Account
        try:
            bankAccount = properties["Account"]["select"]["name"]
        except (KeyError, TypeError):
            bankAccount = None

        objectData = (index, name, value, transaction_type, category, subCategory, date, efectiveValue, bankAccount)

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
df.to_sql(name="FAT_FINANCES", con=engine, if_exists='replace', index=False)
df.to_excel(r"C:\BI\FinancesDB\Finanças.xlsx", index=False)
df.to_csv(r"C:\BI\FinancesDB\FAT_TABLE.csv", index=False)
