from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from app.main import create_app, db
from app.main.util.environment_variables import *
from skywalking import agent, config

IS_USE_SKYWALKING = os.getenv("MIK_USE_SKYWALKING") or ""

if IS_USE_SKYWALKING:
    COLLECTOR_ADDRESS = os.getenv("SW_AGENT_COLLECTOR_BACKEND_SERVICES")
    SERVICE_AGENT_NAME = os.getenv("SW_AGENT_NAME")

    config.init(collector_address=COLLECTOR_ADDRESS + ":11800", service_name=SERVICE_AGENT_NAME)
    config.logging_level = 'DEBUG'
    agent.start()

app = create_app(APP_ENV or "local")

app.app_context().push()

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command("db", MigrateCommand)


@manager.command
def run():
    app.run(host="0.0.0.0")


if __name__ == "__main__":
    manager.run()
