# This script fetches the latest NAV values of tracked mutual funds from the AMFI website and updates them in Firestore.
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import requests
from tqdm import tqdm

# Initialize Firebase
cred = credentials.Certificate("service-account.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
mf_info = db.collection("mutual_funds").document("info")

def fetch_tracked_funds():
    """Fetch tracked funds from Firestore."""
    tracked_fund_data = mf_info.get().to_dict()
    tracked_funds = tracked_fund_data["tracked_funds"]
    
    return tracked_funds

def fetch_latest_fund_values():
    """Fetch the latest NAVs from AMFI website."""
    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    response = requests.get(url)
    nav_data = response.text.splitlines()

    tracked_funds = fetch_tracked_funds()

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

        if scheme_code in tracked_funds:
            data.append([scheme_code, scheme_name, nav_value, nav_date])

    df = pd.DataFrame(data, columns=["Scheme Code", "Scheme Name", "NAV Value", "NAV Date"])

    return df

def update_firestore():
    """Update Firestore with latest fund NAVs."""
    latest_values = fetch_latest_fund_values()
    for idx, row in tqdm(latest_values.iterrows(), total=len(latest_values)):
        scheme_code = row["Scheme Code"]
        doc_ref = mf_info.collection("funds").document(scheme_code)
        doc_ref.set({
            "Scheme Code": scheme_code,
            "Scheme Name": row["Scheme Name"],
            "NAV Value": row["NAV Value"],
            "NAV Date": row["NAV Date"]
        })

if __name__ == "__main__":
    update_firestore()
    print("Firestore updated with latest NAV values.")
