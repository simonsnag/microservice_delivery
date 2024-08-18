import logging
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class MySQLSettings(BaseSettings):
    db_host: str = os.environ.get("MYSQL_HOST", "localhost")
    db_port: str = os.environ.get("MYSQL_PORT", "3306")
    db_name: str = os.environ.get("MYSQL_NAME", "parcel")
    db_user: str = os.environ.get("MYSQL_USER", "root")
    db_pass: str = os.environ.get("MYSQL_PASS", "password")

    @property
    def url(self):
        return f"mysql+aiomysql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"


mysql_settings = MySQLSettings()


class RedisSettings(BaseSettings):
    host: str = os.environ.get("REDIS_HOST", "localhost")
    port: str = os.environ.get("REDIS_PORT", "6379")

    @property
    def url(self):
        return f"redis://{self.host}:{self.port}/"


redis_settings = RedisSettings()


class RabbitSettings(BaseSettings):
    user: str = os.environ.get("RABBIT_USER", "guest")
    password: str = os.environ.get("RABBIT_PASS", "guest")
    host: str = os.environ.get("RABBIT_HOST", "localhost")
    port: str = os.environ.get("RABBIT_PORT", "5672")
    queue_name: str = os.environ.get("RABBIT_QUEUE", "parcel_queue")

    @property
    def url(self):
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}"

        # Для локальных тестов может потребоваться явное указание url
        # return "amqp://guest:guest@localhost:5672"


rabbit_settings = RabbitSettings()


class ADMIN(BaseSettings):
    session: str = os.environ.get("ADMIN_SESSION", "1")


admin = ADMIN()


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler("app.logs", delay=True)
file_handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)
