import gspread
import yaml
import os
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- CONFIG FROM ENV ---
SHEET_ID = os.environ.get("SHEET_ID")
WORKSHEET_NAME = os.environ.get("WORKSHEET_NAME")
SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_CREDENTIALS")

if not (SHEET_ID and WORKSHEET_NAME and SERVICE_ACCOUNT_JSON):
    raise ValueError("SHEET_ID, WORKSHEET_NAME, and GOOGLE_CREDENTIALS must be set as env variables")

# --- LOAD CREDENTIALS ---
creds_dict = json.loads(SERVICE_ACCOUNT_JSON)
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)

# --- LOAD SHEET ---
sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
data = sheet.get_all_records()

# Expected columns: name | score | public_score
members = []
for row in data:
    members.append({
        "name": row["name"],
        "score": int(row["score"]),
        "public_score": int(row["public_score"])
    })

# Sort by score descending
members = sorted(members, key=lambda x: x["score"], reverse=True)

# --- WRITE YAML FILE ---
os.makedirs("_data", exist_ok=True)
with open("_data/whitebelts.yml", "w") as f:
    yaml.dump(members, f, sort_keys=False)

print("Updated rankings file successfully")