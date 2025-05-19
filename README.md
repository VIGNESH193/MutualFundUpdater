# Mutual Fund NAV Updater (GitHub Actions)

This project uses GitHub Actions to run a Python script daily that fetches mutual fund NAVs from AMFI and updates them in Firebase Firestore.

## Setup Instructions

1. Create a Firebase project with Firestore enabled.
2. Generate a service account key (JSON) with Firestore access.
3. Add the JSON key as a GitHub Secret named `FIREBASE_KEY`.
4. Push this repo to GitHub.
5. GitHub Actions will run daily at 7:30 AM IST.
