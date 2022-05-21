import redis
from flask import abort
from flask_restplus import Namespace, Resource
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from simplejson.errors import JSONDecodeError
import requests
import rediscluster
from werkzeug.exceptions import BadRequest
from ..configuration.vault_vars_config import *
from ..database.rediscache import get_redis_host_port

# from google.cloud import bigquery
# from google.cloud import spanner
# from redis.exceptions import RedisError, ResponseError
import psutil
import tracemalloc
import os

from ..util.global_vars import user_agent

api = Namespace(
    "healthcheck",
    description="Confirming the health of the application’s dependencies",
)

tracemalloc.start()
process = psutil.Process(os.getpid())
s = None


@api.route("")
class HealthCheck(Resource):
    @api.doc(responses={200: "Success", 400: "Environment Error"})
    def get(self):
        """
        This endpoint to confirm the health of the application’s dependencies
        """
        try:
            try:
                rec_mongo_client = MongoClient(
                    REC_DB_URI, serverSelectionTimeoutMS=5000, connectTimeoutMS=20000
                )
                rec_mongo_client.server_info()
                rec_mongo_connection_status = "OK"
            except ServerSelectionTimeoutError:
                rec_mongo_connection_status = "FAIL"

            try:
                glb_mongo_client = MongoClient(
                    GLB_DB_URI, serverSelectionTimeoutMS=5000, connectTimeoutMS=20000
                )
                glb_mongo_client.server_info()
                glb_mongo_connection_status = "OK"
            except ServerSelectionTimeoutError:
                glb_mongo_connection_status = "FAIL"

            # try:
            #     bigquery.Client.from_service_account_json(BIGQUERY_CREDENTIAL)
            #     bigquery_connection_status = "OK"
            # except ValueError:
            #     bigquery_connection_status = "FAIL"
            #
            # try:
            #     spanner.Client.from_service_account_json(SPANNER_CREDENTIAL)
            #     spanner_connection_status = "OK"
            # except ValueError:
            #     spanner_connection_status = "FAIL"

            try:
                if REDIS_MODE == "sentinel":
                    redis_host, redis_port = get_redis_host_port(
                        REDIS_HOST_STR, REDIS_PORT, REDIS_MASTER
                    )
                    test_redis_client = redis.StrictRedis(
                        host=redis_host,
                        port=redis_port,
                        password=REDIS_PASSWORD,
                        db=REDIS_DATABASE,
                    )
                elif REDIS_MODE == "cluster":
                    redis_start_nodes = [
                        dict({"host": host, "port": REDIS_PORT})
                        for host in REDIS_HOST_STR.split(",")
                    ]
                    test_redis_client = rediscluster.RedisCluster(
                        startup_nodes=redis_start_nodes, password=REDIS_PASSWORD
                    )
                else:
                    raise ValueError("The input redis mode is invalid")

                test_redis_client.ping()
                redis_connection_status = "OK"
            except Exception:
                redis_connection_status = "FAIL"

            try:
                requests.put(
                    PROFANITY_SCREEN_API,
                    json=["test"],
                    headers={"User-Agent": user_agent},
                ).json()
                profanity_screen_api_status = "OK"
            except JSONDecodeError:
                profanity_screen_api_status = "FAIL"

            try:
                requests.post(
                    STORE_NAME_DUP_CHECK_API,
                    json={"suggestStoreNames": ["test"]},
                    headers={"User-Agent": user_agent},
                ).json()
                store_name_dup_api_status = "OK"
            except JSONDecodeError:
                store_name_dup_api_status = "FAIL"

            if "FAIL" in (
                rec_mongo_connection_status,
                glb_mongo_connection_status,
                # bigquery_connection_status,
                # spanner_connection_status,
                redis_connection_status,
                profanity_screen_api_status,
                store_name_dup_api_status,
            ):
                healthcheck_status = "FAIL"
            else:
                healthcheck_status = "OK"

            response = {
                "app_name": APP_PROJ + "-" + APP_ENV + "-" + APP_NAME,
                "version": APP_VERSION,
                "healthcheck": healthcheck_status,
                "db_resources": {
                    "rec_mongo_db": rec_mongo_connection_status,
                    "glb_mongo_db": glb_mongo_connection_status,
                    # "bigquery": bigquery_connection_status,
                    # "spanner": spanner_connection_status,
                    "redis": redis_connection_status,
                },
                "external_api_resources": {
                    "profanity_screen_api": profanity_screen_api_status,
                    "store_name_dup_api": store_name_dup_api_status,
                },
            }
            return response
        except EnvironmentError as err:
            abort(400, BadRequest(err))


@api.route("/memory")
class GetCurrentMemoryUsage(Resource):
    @api.doc(responses={200: "Success", 400: "Environment Error"})
    def get(self):
        return {"memory": process.memory_info().rss / 1048576}


@api.route("/snapshot")
class GetMemorySnapshot(Resource):
    @api.doc(responses={200: "Success", 400: "Environment Error"})
    def get(self):
        global s
        if not s:
            s = tracemalloc.take_snapshot()
            return "taken snapshot\n"
        else:
            lines = []
            top_stats = tracemalloc.take_snapshot().compare_to(s, "lineno")
            for stat in top_stats[:5]:
                lines.append(str(stat))
            s = tracemalloc.take_snapshot()
            return "\n".join(lines)
