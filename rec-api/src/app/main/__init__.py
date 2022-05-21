from flask import Flask, Blueprint
from flask_bcrypt import Bcrypt

from .config import config_by_name
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_restplus import Api

from app.main.util.global_db_connection import (
    rec_db_conn,
    glb_db_conn,
    crm_db_conn,
    # bigquery_client,
    redis_client,
)
from app.main.util.global_vars import names_set, text_clean
from app.main.util.global_models import logistic_regression, scaler
from app.main.controller.michaels_controller import api as michaels_ns
from app.main.controller.mktplace_controller import api as mktplace_ns
from app.main.controller.ping_version_controller import api as ping_version_ns
from app.main.controller.healthcheck_controller import api as healthcheck_ns
from app.main.controller.b2b_ent_controller import api as b2b_ent_ns
from app.main.controller.b2b_edu_controller import api as b2b_edu_ns
from app.main.controller.store_name_controller import api as store_name_ns
from app.main.controller.word_embedding_controller import api as word_embedding_ns
from app.main.controller.crm_controller import api as crm_ns

from app.main.database.mongodb import db
from app.main.database.cache import cache

flask_bcrypt = Bcrypt()


blueprint = Blueprint("api", __name__, url_prefix="/api/rec")

authorizations = {
    "fgm_token": {"type": "apiKey", "in": "header", "name": "Authorization"}
}

api = Api(
    blueprint,
    title="Michaels Recommendation API",
    version="1.0.293 beta",
    description="Michaels Recommendation Engine Flask Restplus Web Service",
    authorizations=authorizations,
    doc="/doc/",
)


api.add_namespace(michaels_ns, path="/michaels")
api.add_namespace(mktplace_ns, path="/mktplace")
api.add_namespace(b2b_ent_ns, path="/b2b_ent")
api.add_namespace(b2b_edu_ns, path="/b2b_edu")
api.add_namespace(ping_version_ns, path="/ping")
api.add_namespace(healthcheck_ns, path="/healthcheck")
api.add_namespace(store_name_ns, path="/store_name")
api.add_namespace(word_embedding_ns, path="/word_embedding")
api.add_namespace(crm_ns, path="/crm")


def create_app(config_name):
    app = Flask(__name__)
    cache.init_app(app)
    app.register_blueprint(blueprint)
    if config_name in config_by_name:
        app_config = config_by_name[config_name]
    else:
        app_config = config_by_name["tst00"]
    app.config.from_object(app_config)
    app.config["ERROR_404_HELP"] = False
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    if config_name != "test":
        db.init_app(app)
    flask_bcrypt.init_app(app)

    return app
