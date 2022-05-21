from google.cloud import bigquery


def create_bigquery_client(credential_path: str):
    """
    This function is used to connect to Google BigQuery to get recently_view data
    """
    bigquery_client = bigquery.Client.from_service_account_json(credential_path)
    return bigquery_client
