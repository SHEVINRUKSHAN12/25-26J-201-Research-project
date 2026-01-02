import firebase_admin
from firebase_admin import credentials, firestore
import os

# Path to the service account key
# Assuming it's in the root of the backend directory, two levels up from this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CRED_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")

def initialize_firebase():
    """Initializes Firebase Admin SDK if not already initialized."""
    try:
        if not firebase_admin._apps:
            if os.path.exists(CRED_PATH):
                cred = credentials.Certificate(CRED_PATH)
                firebase_admin.initialize_app(cred)
                print("Firebase Admin SDK initialized successfully.")
            else:
                print(f"Warning: serviceAccountKey.json not found at {CRED_PATH}")
                print("Backend database features will not work until the key is added.")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")

def get_db():
    """Returns the Firestore client."""
    initialize_firebase()
    return firestore.client()
