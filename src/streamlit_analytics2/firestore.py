import streamlit as st
from google.cloud import firestore
import logging


def sanitize_data(data):
    if isinstance(data, dict):
        # Recursively sanitize dictionary keys
        return {str(k) if k else '': sanitize_data(v) for k, v in data.items() if k}
    elif isinstance(data, list):
        # Apply sanitization to elements in lists
        return [sanitize_data(item) for item in data]
    else:
        return data

def load(counts, service_account_json, collection_name):
    st.write("loading")
    st.write(counts)
    """Load count data from firestore into `counts`."""
    db = firestore.Client.from_service_account_json(service_account_json)
    col = db.collection(collection_name)
    firestore_counts = col.document("counts").get().to_dict()

    if firestore_counts is not None:
        for key in firestore_counts:
            if key in counts:
                counts[key] = firestore_counts[key]
    
    # Log loaded data for debugging
    logging.debug("Data loaded from Firestore: %s", firestore_counts)

def save(counts, service_account_json, collection_name):
    st.write("loading")
    st.write(counts)
    """Save count data from `counts` to firestore."""
    # Ensure all keys are strings and not empty
    sanitized_counts = sanitize_data(counts)
    
    db = firestore.Client.from_service_account_json(service_account_json)
    col = db.collection(collection_name)
    doc = col.document("counts")
    
    # Log the data being saved
    logging.debug("Data being saved to Firestore: %s", sanitized_counts)

    # Attempt to save to Firestore
    doc.set(sanitized_counts)  # creates if doesn't exist
