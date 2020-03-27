from google.cloud import firestore
from google.auth.exceptions import DefaultCredentialsError
import os


def get_vars(name):
    if os.getenv("GAE_ENV", "").startswith("standard"):
        try:
            db = firestore.Client()
            doc_ref = db.collection(u"env_vars").document(u"env_prod")
            doc = doc_ref.get().to_dict()
            return doc[name]
        except DefaultCredentialsError:
            # not in gcp env : for migration purpose
            return os.getenv(name)
    return os.getenv(name)
