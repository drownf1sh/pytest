import pytest
import pymongo

from app.main.database.mongodb import PymongoConnection


class TestPymongoConnection:
    def test_pymongo_connection(self):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        test_db = client["test"]
        collection = test_db["test_col"]
        collection.insert_many([{}])
        connection = PymongoConnection(db_name="test_db", collection_name="test_col")
        assert connection.connection_status
        assert connection.database_name == "test"
        assert connection.collection_name == "test_col"
        assert (
            str(type(connection.get_database_instance()))
            == "<class 'pymongo.database.Database'>"
        )
        assert (
            str(type(connection.get_collection_instance()))
            == "<class 'pymongo.collection.Collection'>"
        )
        client.drop_database("test")


if __name__ == "__main__":
    pytest.main()
