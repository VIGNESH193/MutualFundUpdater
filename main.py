import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import requests

# Initialize Firebase
cred = credentials.Certificate("service-account.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def fetch_latest_fund_values():
    """Fetch the latest NAVs from AMFI website."""
    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    response = requests.get(url)
    nav_data = response.text.splitlines()

    data = []
    for line in nav_data[1:]:
        parts = line.strip().split(';')
        if len(parts) < 6:
            continue
        scheme_code = parts[0].strip()
        scheme_name = parts[3].strip()
        nav_value = parts[4].strip()
        nav_date = parts[5].strip()
        nav_date = pd.to_datetime(nav_date, dayfirst=True).strftime('%d-%m-%Y')

        data.append([scheme_code, scheme_name, nav_value, nav_date])

    df = pd.DataFrame(data, columns=["Scheme Code", "Scheme Name", "NAV Value", "NAV Date"])

    return df

def update_firestore():
    """Update Firestore with latest fund NAVs."""
    latest_values = fetch_latest_fund_values()
    for idx, row in latest_values.iterrows():
        scheme_code = row["Scheme Code"]
        doc_ref = db.collection("mf_amfiindia").document(scheme_code)
        doc = doc_ref.get()
        if not doc.exists:
            doc_ref.set({
                "Scheme Code": scheme_code,
                "Scheme Name": row["Scheme Name"],
            })
        date_ref = doc_ref.collection("history").document(row["NAV Date"])
        date_ref.set({
            "NAV Value": row["NAV Value"]
        })

if __name__ == "__main__":
    update_firestore()
