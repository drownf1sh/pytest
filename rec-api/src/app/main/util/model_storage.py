import datetime
import pickle
from bson import ObjectId
from gridfs.errors import NoFile
from app.main.database.mongodb import PymongoConnection
import gridfs


def save_model(model, model_name: str, db_name: str, collection_name: str):
    """Save model to database

    Parameters
    ----------
    model: ML Model
        The trained ML model you want to save into database
    model_name: str
        The model's name. You can use existing model's name and only the latest one will be retrieved from database
        later when you call load_model function with the model's name
    db_name: str
        The name of the data used to save model
    collection_name: str
        The name of the collection used to save model info

    Returns
    -------
    object_id: str
        The object ID for saved model in database, which can be used to retrieve the model later

    Examples
    -------
    >>> from src.app.main.util.model_storage import save_model
    >>> streaming_cbf_pipeline = save_model(
    ...               model=sample_model,
    ...               model_name="sample_model_name",
    ...               db_name="database_name",
    ...               collection_name="collection_name")
    >>> streaming_cbf_pipeline.predict(sample_data)
    """
    rec_db_connection = PymongoConnection(db_name, collection_name)
    rec_db_instance = rec_db_connection.get_database_instance()
    rec_db_collection = rec_db_connection.get_collection_instance()
    fs = gridfs.GridFS(rec_db_instance)
    object_id = fs.put(pickle.dumps(model), file_name=model_name)
    rec_db_collection.insert_one(
        {
            "model": model_name,
            "object_id": object_id,
            "created_time": datetime.datetime.now(),
        }
    )
    rec_db_connection.connection.close()
    return object_id


def load_model(
    db_name: str,
    collection_name: str,
    model: str = None,
    object_id: str = None,
):
    """Retrieve model from database

    Parameters
    ----------
    db_name: str
        The database name
    collection_name: str
        The name of collection that stores model reference info.
    model: str, default = None
        The name of the model that will be retrieved from db. The latest model with this
        name will be returned. Only one of model or object_id is needed.
    object_id: str, default = None
        The object_id of the model that will be retrieved from db. The specific model
        with this object_id will be returned. Only one of model or object_id is needed.

    Returns
    -------
    model: ML model
        The retrieved ML model

    Examples
    -------
    >>> from src.app.main.util.model_storage import load_model
    >>> streaming_cbf_pipeline = load_model(
    ...               db_name="database_name",
    ...               collection_name="collection_name", model="streaming_cbf_pipeline")
    >>> streaming_cbf_pipeline.predict(sample_data)
    """

    rec_db_connection = PymongoConnection(db_name, collection_name)
    rec_db_instance = rec_db_connection.get_database_instance()
    rec_db_collection = rec_db_connection.get_collection_instance()
    fs = gridfs.GridFS(rec_db_instance)

    if not model and not object_id:
        print("At least one of model nad objectID is required to retrieve model")
        return None
    elif model and not object_id:
        try:
            object_id = rec_db_collection.find_one(
                {"model": model}, sort=([("created_time", -1)])
            )["object_id"]
        except TypeError as e:
            print("Model Does Not Exist In Database")
            raise e

    try:
        retrieved_model = pickle.load(fs.get(ObjectId(object_id)))
    except NoFile as e:
        print("Model Object ID Does Not Exist In Database")
        raise e

    rec_db_connection.connection.close()
    return retrieved_model


def remove_model(
    db_name: str,
    collection_name: str,
    model: str = None,
    object_id: str = None,
):
    """
    Parameters
    ----------
    db_name: str
        The database name
    collection_name: str
        The name of collection that stores model reference info.
    model: str. default = None
        The name of the model that will be retrieved from db. The latest model with this
        name will be returned. Only one of model or object_id is needed.
    object_id: str default = None
        The object_id of the model that will be retrieved from db. The specific model
        with this object_id will be returned. Only one of model or object_id is needed.

    Examples
    -------
    >>> from app.main.util.model_storage import remove_model
    >>> remove_model(db_name="database_name",
    ...              collection_name="collection_name", model="streaming_cbf_pipeline")
    Models with following object id have been deleted from database:
    ['6053663b7ff66c4d60b512cc']

    """

    rec_db_connection = PymongoConnection(db_name, collection_name)
    rec_db_instance = rec_db_connection.get_database_instance()
    rec_db_collection = rec_db_connection.get_collection_instance()

    if not model and not object_id:
        print("At least one of model or objectID is required to retrieve model")
        return None
    elif model and not object_id:
        try:
            latest_object_id = rec_db_collection.find_one(
                {"model": model}, sort=([("created_time", -1)])
            )["object_id"]
            object_id_list = []
            for model_object in rec_db_collection.find({"model": model}):
                if model_object["object_id"] != latest_object_id:
                    object_id_list.append(str(model_object["object_id"]))
        except TypeError as e:
            print("Model Does Not Exist In Database")
            raise e
    else:
        object_id_list = [object_id]

    for object_id in object_id_list:
        _remove_model_on_id(object_id, rec_db_instance, collection_name)

    print(
        "Models with following object id have been deleted from database:\n"
        + str(object_id_list)
    )

    rec_db_connection.connection.close()
    return object_id_list


def _remove_model_on_id(object_id: str, db_instance, collection_name):
    """
    Parameters
    ----------
    object_id: str
        The model object_id that will be deleted
    """
    rec_models_instance = db_instance[collection_name]
    fs_files_instance = db_instance["fs.files"]
    fs_chunks_instance = db_instance["fs.chunks"]

    rec_models_instance.delete_one({"object_id": ObjectId(object_id)})
    fs_files_instance.delete_one({"_id": ObjectId(object_id)})
    fs_chunks_instance.delete_many({"files_id": ObjectId(object_id)})
