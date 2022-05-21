from google.cloud import spanner


def create_spanner_client(credential_path: str):
    """
    This function is used to connect to Google spanner to get events data
    """
    spanner_client = spanner.Client.from_service_account_json(credential_path)
    return spanner_client
