import requests
import json
import pandas

with open("config.json", "r") as archive:
    config_json = json.load(archive)

# Acess Credential
secret = config_json["Internal Integratin Secret"]
