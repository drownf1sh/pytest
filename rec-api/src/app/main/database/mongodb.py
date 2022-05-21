from flask_mongoengine import MongoEngine
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from app.main.configuration.database_config import db_list
from app.main.configuration.vault_vars_config import (
    MAX_POOL_SIZE,
    MIN_POOL_SIZE,
    MAX_IDLE_TIME_MS,
    SOCKET_TIMEOUT_MS,
    CONNECT_TIMEOUT_MS,
    SERVER_SELECTION_TIMEOUT_MS,
)

"""
This object is used to create database mapping object in model folder
"""
db = MongoEngine()


class PymongoConnection:
    """
    This class is used to do quick connection or query checking
    """

    def __init__(self, db_name: str, collection_name: str = None):
        """
        This is initialization function.
        Check db_name first then call create_connection()
        to create db connection instance
        Note: Must have db_name in given URI
        :param db_name: str
            The name of target database, must be in db_list
        :param collection_name: str, default=None
            Provide name of target collection(optional)
        """
        assert db_name in db_list, "Given db_name is not in db_list"
        self.collection_name = collection_name
        self.connection = self._create_connection(db_name)

    def _create_connection(self, db_name):
        """
        Create connection instance also check
        if the db is connected
        :return: mongo_client instance
        """
        try:
            mongo_client = MongoClient(
                db_list[db_name],
                maxPoolSize=MAX_POOL_SIZE,
                minPoolSize=MIN_POOL_SIZE,
                maxIdleTimeMS=MAX_IDLE_TIME_MS,
                socketTimeoutMS=SOCKET_TIMEOUT_MS,
                connectTimeoutMS=CONNECT_TIMEOUT_MS,
                serverSelectionTimeoutMS=SERVER_SELECTION_TIMEOUT_MS,
            )
            mongo_client.server_info()
            self.database_name = mongo_client.get_database().name
            self.connection_status = True
            return mongo_client
        except ServerSelectionTimeoutError:
            self.connection_status = False

    def get_database_instance(self):
        """
        Get database instance by given db_name
        :return: pymongo database instance
        """
        if not self.connection_status:
            raise ServerSelectionTimeoutError
        return self.connection[self.database_name]

    def get_collection_instance(self):
        """
        Get collection instance by given collection_name
        :return: pymongo collection instance
        """
        if not self.connection_status:
            raise ServerSelectionTimeoutError
        if (
            self.collection_name
            in self.connection[self.database_name].list_collection_names()
        ):
            return self.connection[self.database_name][self.collection_name]
        else:
            raise ValueError("This collection name is incorrect")
