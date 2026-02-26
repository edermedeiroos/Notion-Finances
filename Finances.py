import requests
import json
import pandas
import openpyxl
import sqlalchemy

# ----------------------------------------------------------------------------
#             PERSONAL FINANCES - ETL
#
# 1) Load config json (DB & API Credentials)
# 2) Connection to DB mysql
# 3) Request to notion API
# 4) While True loop to get all pages from endpoint (with validation)
# 5) Type definition and extract items from response
# 6) DataFrame Creation and Export (csv, xlxs and DB)
# ----------------------------------------------------------------------------

with open("config.json", "r") as archive:
    configJson = json.load(archive)

DB_USER = configJson.get("DB_USER")
DB_PASSWORD = configJson.get("DB_PASSWORD")
DB_HOST = configJson.get("DB_HOST")
DB_PORT = configJson.get("DB_PORT")
DB_DATABASE = configJson.get("DB_DATABASE")

engine = sqlalchemy.create_engine(
    f"mysql+mysqldb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
)

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

dscRequest = requests.post(url=urlDataSourceQuery, json=bodyDataSourceQuery, headers=AUTH_HEADERS)
dscJson = dscRequest.json()

notionData = []
notionColumns = ["ID", "NAME", "VALUE", "TYPE", "CATEGORY", "SUB_CATEGORY", "DATE", "EFECTIVE_VALUE", "ACCOUNT"]
index = 1

while True:
    for item in dscJson["results"]:
        properties = item["properties"]
        
        try:
            name = properties["Name"]["title"][0]["plain_text"]
        except (KeyError, IndexError, TypeError):
            name = "Sem Título"

        try:
            value = round(float(properties["Value"]["number"]), 2)
        except (KeyError, TypeError):
            value = 0.0

        try:
            transaction_type = properties["Type"]["select"]["name"]
        except (KeyError, TypeError):
            transaction_type = None

        try:
            category = properties["Category"]["select"]["name"]
        except (KeyError, TypeError):
            category = None

        try:
            subCategory = properties["Sub Category"]["select"]["name"]
        except (KeyError, TypeError, AttributeError):
            subCategory = None

        try:
            date = properties["Date"]["date"]["start"]
        except (KeyError, TypeError):
            date = None

        try:
            efectiveValue = properties["Effective Value"]["formula"]["number"]
        except (KeyError, TypeError):
            efectiveValue = 0.0

        try:
            bankAccount = properties["Account"]["select"]["name"]
        except (KeyError, TypeError):
            bankAccount = None

        objectData = (index, name, value, transaction_type, category, subCategory, date, efectiveValue, bankAccount)
        notionData.append(objectData)
        index += 1

    if dscJson["has_more"]:
        next_cursor = dscJson["next_cursor"]
        bodyDataSourceQuery["start_cursor"] = next_cursor

        dscRequest = requests.post(url=urlDataSourceQuery, 
                            json=bodyDataSourceQuery,
                            headers=AUTH_HEADERS
                            )
        dscJson = dscRequest.json()
    
    else:
        break

df_notion = pandas.DataFrame(notionData, columns=notionColumns)

df_notion.to_sql(name="FAT_FINANCES", con=engine, if_exists='replace', index=False)
df_notion.to_excel(r"C:\BI\FinancesDB\Finanças.xlsx", index=False)
df_notion.to_csv(r"C:\BI\FinancesDB\FAT_TABLE.csv", index=False)
