"""
This module provides functions to load data from database.
"""
import mysql.connector
import pandas as pd
import pymongo


def mongo_db_reader(
    db_address: str,
    db_name: str,
    collection_name: str,
    db_username: str = None,
    db_password: str = None,
    query: dict = {},
    no_id: bool = True,
):
    """
    This function is to load data from mongoDB.

    Parameters
    ----------
    db_address: str
        The target MongoDB address.
    db_name: str
        The target database name.
    collection_name: str
        The target collection name.
    db_username: str, default = None
        The user name of the MongoDB client.
    db_password: str, default = None
        The password of the MongoDB client.
    query: dict, default = {}
        The query to extract data.
    no_id: bool, default = True
        Specify remove id or not.

    Returns
    -------
    df: pd.DataFrame
        The mongoDB data in dataframe format

    Example
    -------
    >>> from app.main.recommender.load._db_reader import mongo_db_reader
    >>> df = mongo_db_finder(
    ...     db_address="mongodb://localhost:30277/",
    ...     db_name="test_db",
    ...     collection_name="test_col",
    ...     query={},
    ...     db_username="root",
    ...     db_password="R00tPassword!")
    """

    # assertion
    assert isinstance(db_address, str), "db_address must be str"
    assert isinstance(db_name, str), "db_name must be str"
    assert isinstance(collection_name, str), "collection_name must be str"
    if db_username is not None:
        assert isinstance(db_username, str), "db_username must be str"
    if db_password is not None:
        assert isinstance(db_password, str), "db_password must be str"
    assert isinstance(query, dict), "query must be dict"
    assert isinstance(no_id, bool), "no_id must be bool"

    # Connect to MongoDB.
    if db_username and db_password:
        client = pymongo.MongoClient(
            db_address, username=db_username, password=db_password
        )
    else:
        client = pymongo.MongoClient(db_address)
    db = client[db_name]
    collection = db[collection_name]

    # save data to dataframe
    df = pd.DataFrame(list(collection.find(query)))

    # drop id
    if no_id:
        df = df.drop("_id", axis=1)

    return df


def mysql_db_reader(
    host: str,
    database: str = None,
    username: str = None,
    password: str = None,
    query: str = None,
    port: int = 3306,
):
    """
    This function is to load data from MySQL.

    Parameters
    ----------
    host: str
        The target MySQL host.
    database: str, default = None
        The target database name.
    username: str, default = None
        The user name of the MySQL database.
    password: str, default = None
        The password of the MySQL database.
    query: str, default = None
        The query to extract data.
    port: int, default = 3306
        The port number.

    Returns
    -------
    df: pd.DataFrame
        The MySQL data in dataframe format

    Example
    -------
    >>> from app.main.recommender.load._db_reader import mysql_db_reader
    >>> df = mysql_db_reader(
    ...     host="127.0.0.1",
    ...     database="test_db",
    ...     username="user1",
    ...     password="user1_password",
    ...     query="select count(*) from test_db.table1",
    ...     port=30360)
    """

    # assertion
    assert isinstance(host, str), "host must be str"
    if database is not None:
        assert isinstance(database, str), "database must be str"
    if username is not None:
        assert isinstance(username, str), "username must be str"
    if password is not None:
        assert isinstance(password, str), "password must be str"
    if query is not None:
        assert isinstance(query, str), "query must be str"
    assert isinstance(port, int), "port must be int"

    # Connect to database.
    mydb = mysql.connector.connect(
        host=host, port=port, database=database, user=username, password=password
    )

    # save data to dataframe
    df = pd.read_sql(query, mydb)

    return df
