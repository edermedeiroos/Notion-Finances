import requests
import pandas as pd
import os

# ----------------------------------------------------------------------------
#                         NOTION FINANCES - ETL
#
# 1) Load .env (API Credentials)
# 3) Request to notion API
# 4) While True loop to get all pages from endpoint (with validation)
# 5) Type definition and extract items from response
# 6) DataFrame creation
# ----------------------------------------------------------------------------

NOTION_SECRET = os.getenv("NOTION_INTERNAL_INTEGRATION_SECRET")
NOTION_DS_ID = "25b22a3e-ef57-8147-ae65-000b8dd610e3"

notion_url = f"https://api.notion.com/v1/data_sources/{NOTION_DS_ID}/query"
notion_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {NOTION_SECRET}",
    "Notion-Version": "2025-09-03"
}
notion_body = {
    "sorts": [
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
notion_request = requests.post(url=notion_url, json=notion_body, headers=notion_headers)
notion_json = notion_request.json()
notion_data = []
notion_columns = ["ID", "NAME", "VALUE", "TYPE", "CATEGORY", "SUB_CATEGORY", "DATE", "EFECTIVE_VALUE", "ACCOUNT"]

while True:
    for item in notion_json["results"]:
        properties = item["properties"]
        
        id = item.get("id")

        try:
            name = properties["Name"]["title"][0]["plain_text"]
        except (KeyError, IndexError, TypeError):
            name = "Sem Título"

        try:
            value = properties["Value"]["number"]
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
            sub_category = properties["Sub Category"]["select"]["name"]
        except (KeyError, TypeError, AttributeError):
            sub_category = None

        try:
            date = properties["Date"]["date"]["start"]
        except (KeyError, TypeError):
            date = None

        try:
            effective_value = properties["Effective Value"]["formula"]["number"]
        except (KeyError, TypeError):
            effective_value = 0.0

        try:
            account = properties["Account"]["select"]["name"]
        except (KeyError, TypeError):
            account = None

        object_data = (id, name, value, transaction_type, category, sub_category, date, effective_value, account)
        notion_data.append(object_data)

    if notion_json["has_more"]:
        next_cursor = notion_json["next_cursor"]
        notion_body["start_cursor"] = next_cursor

        notion_request = requests.post(url=notion_url, json=notion_body, headers=notion_headers)
        notion_json = notion_request.json()
    
    else:
        break

df_notion = pd.DataFrame(notion_data, columns=notion_columns)
