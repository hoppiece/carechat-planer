from google.cloud import firestore


def get_user_state(line_identifier: str) -> dict:
    db = firestore.Client()
    user_state = db.collection("users").document(line_identifier).get().to_dict()
    return user_state
