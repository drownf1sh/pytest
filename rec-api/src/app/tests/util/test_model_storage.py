# """
# Test for loading model to database
# Commented out because no API is using model related functions
# """
# import datetime
# import operator
# import pickle
#
# from bson import ObjectId
# import gridfs
# import pytest
# from gridfs.errors import NoFile
# from pymongo import MongoClient
#
# from app.main.util.model_storage import load_model, save_model, remove_model
#
#
# class TestModelStorage:
#
#     test_data = [1, 2, 3]
#     model_name = "test_data"
#     db_uri = "mongodb://localhost:27017/"
#     db_name = "test"
#     db_ref = "test_db"
#     collection_name = "test_col"
#
#     def test_load_model_with_model_name(self):
#         """Test load data from mongodb with model_name"""
#         # Save data to database
#         db_connection = MongoClient(self.db_uri)
#         db_instance = db_connection[self.db_name]
#         db_collection = db_instance[self.collection_name]
#         fs = gridfs.GridFS(db_instance)
#
#         object_id = fs.put(pickle.dumps(self.test_data), file_name=self.model_name)
#         db_collection.insert_one(
#             {
#                 "model": self.model_name,
#                 "object_id": object_id,
#                 "created_time": datetime.datetime.now(),
#             }
#         )
#
#         # Load data from database via load_model
#         loaded_date = load_model(
#             db_name=self.db_ref,
#             collection_name=self.collection_name,
#             model=self.model_name,
#         )
#         db_collection.drop()
#         db_connection.close()
#         assert operator.eq(loaded_date, self.test_data)
#
#     def test_load_model_with_model_name_not_exist(self):
#         """Test load data from mongodb with model_name"""
#         # Save data to database
#         db_connection = MongoClient(self.db_uri)
#         db_instance = db_connection[self.db_name]
#         db_collection = db_instance[self.collection_name]
#         fs = gridfs.GridFS(db_instance)
#
#         object_id = fs.put(pickle.dumps(self.test_data), file_name=self.model_name)
#         db_collection.insert_one(
#             {
#                 "model": self.model_name,
#                 "object_id": object_id,
#                 "created_time": datetime.datetime.now(),
#             }
#         )
#
#         # Load data from database via load_model
#         try:
#             load_model(
#                 db_name=self.db_ref,
#                 collection_name=self.collection_name,
#                 model="SomeWeirdModelName",
#             )
#         except TypeError:
#             assert True
#         else:
#             assert False
#         db_collection.drop()
#         db_connection.close()
#
#     def test_load_model_with_object_id(self):
#         """Test load data from mongodb with object_id"""
#         db_connection = MongoClient(self.db_uri)
#         db_instance = db_connection[self.db_name]
#         db_collection = db_instance[self.collection_name]
#         fs = gridfs.GridFS(db_instance)
#
#         object_id = fs.put(pickle.dumps(self.test_data), file_name=self.model_name)
#         db_collection.insert_one(
#             {
#                 "model": self.model_name,
#                 "object_id": object_id,
#                 "created_time": datetime.datetime.now(),
#             }
#         )
#
#         loaded_date = load_model(
#             db_name=self.db_ref,
#             collection_name=self.collection_name,
#             object_id=object_id,
#         )
#         db_collection.drop()
#         db_connection.close()
#         assert operator.eq(loaded_date, self.test_data)
#
#     def test_load_model_with_object_id_not_exit(self):
#         """Test load data from mongodb with object_id"""
#         db_connection = MongoClient(self.db_uri)
#         db_instance = db_connection[self.db_name]
#         db_collection = db_instance[self.collection_name]
#         fs = gridfs.GridFS(db_instance)
#
#         object_id = fs.put(pickle.dumps(self.test_data), file_name=self.model_name)
#         db_collection.insert_one(
#             {
#                 "model": self.model_name,
#                 "object_id": object_id,
#                 "created_time": datetime.datetime.now(),
#             }
#         )
#
#         try:
#             load_model(
#                 db_name=self.db_ref,
#                 collection_name=self.collection_name,
#                 object_id="abcdefabcdefabcdefabcdef",
#             )
#         except NoFile:
#             assert True
#         else:
#             assert False
#         db_collection.drop()
#         db_connection.close()
#
#     def test_save_model(self):
#         db_connection = MongoClient(self.db_uri)
#         db_instance = db_connection[self.db_name]
#         db_collection = db_instance[self.collection_name]
#         db_collection.insert_one({})
#         fs = gridfs.GridFS(db_instance)
#
#         # Save data into database via save_model
#         object_id = save_model(
#             self.test_data,
#             self.model_name,
#             self.db_ref,
#             self.collection_name,
#         )
#
#         # Load data from database to compare
#         loaded_data = pickle.load(fs.get(ObjectId(object_id)))
#
#         db_collection.drop()
#         db_connection.close()
#         assert operator.eq(loaded_data, self.test_data)
#
#     def test_remove_model_with_model_name(self):
#         # Save data into database
#         db_connection = MongoClient(self.db_uri)
#         db_instance = db_connection[self.db_name]
#         db_collection = db_instance[self.collection_name]
#         db_collection.insert_one({})
#         fs = gridfs.GridFS(db_instance)
#
#         # Insert two data entries with same model_name, and the first one will be
#         # deleted
#         object_id_1 = fs.put(pickle.dumps(self.test_data), file_name=self.model_name)
#         db_collection.insert_one(
#             {
#                 "model": self.model_name,
#                 "object_id": object_id_1,
#                 "created_time": datetime.datetime.now(),
#             }
#         )
#
#         object_id_2 = fs.put(pickle.dumps(self.test_data), file_name=self.model_name)
#         db_collection.insert_one(
#             {
#                 "model": self.model_name,
#                 "object_id": object_id_2,
#                 "created_time": datetime.datetime.now(),
#             }
#         )
#
#         removed_object_id = remove_model(
#             self.db_ref, self.collection_name, model=self.model_name
#         )
#
#         count = db_collection.count_documents({"model": self.model_name})
#         db_collection.drop()
#         db_connection.close()
#         assert operator.eq(count, 1)
#         assert operator.eq(removed_object_id[0], str(object_id_1))
#
#     def test_remove_model_with_object_id(self):
#         # Save data into database
#         db_connection = MongoClient(self.db_uri)
#         db_instance = db_connection[self.db_name]
#         db_collection = db_instance[self.collection_name]
#         db_collection.insert_one({})
#         fs = gridfs.GridFS(db_instance)
#
#         # Insert two data entries with same model_name, and the first one will be
#         # deleted
#         object_id_1 = fs.put(pickle.dumps(self.test_data), file_name=self.model_name)
#         db_collection.insert_one(
#             {
#                 "model": self.model_name,
#                 "object_id": object_id_1,
#                 "created_time": datetime.datetime.now(),
#             }
#         )
#
#         object_id_2 = fs.put(pickle.dumps(self.test_data), file_name=self.model_name)
#         db_collection.insert_one(
#             {
#                 "model": self.model_name,
#                 "object_id": object_id_2,
#                 "created_time": datetime.datetime.now(),
#             }
#         )
#
#         removed_object_id = remove_model(
#             self.db_ref, self.collection_name, object_id=object_id_2
#         )
#         count = db_collection.count_documents({"model": self.model_name})
#         db_collection.drop()
#         db_connection.close()
#         assert operator.eq(count, 1)
#         assert operator.eq(removed_object_id[0], object_id_2)
#
#
# if __name__ == "__main__":
#     pytest.main()
