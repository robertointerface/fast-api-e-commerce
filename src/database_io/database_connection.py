import os
from abc import ABC, abstractmethod
import pymongo
import urllib
from boto3 import Session
from botocore.credentials import ReadOnlyCredentials

MONGO_CONNECTION = None
SYNC_MONGO_CONNECTION = None
MONGO_CONNECTION_PORT = 27017
ECOMMERCE_DATABASE_NAME = os.environ['ECOMMERCE_DATABASE_NAME']
DATABASE_CLUSTER_DOMAIN = os.environ['DATABASE_CLUSTER_DOMAIN']


class MongoDbConnection(ABC):

    @abstractmethod
    def get_connection_string(self):
        pass


class MongoDbLocalConnection(MongoDbConnection):

    def get_connection_string(self):
        return f'mongodb://localhost:{MONGO_CONNECTION_PORT}'


def get_current_user_or_role_credentials() -> ReadOnlyCredentials:
    """Returns AWS read only credentials for either the current user or the current IAM role executed on the server.

    Returns:
        A set of frozen credentials constituting an access key, a secret key and a token.
    """
    session = Session()
    credentials = session.get_credentials()

    # Credentials are refreshable, so accessing your access key / secret key
    # separately can lead to a race condition. Use this to get an actual matched set.
    return credentials.get_frozen_credentials()


class MongoDbConnectByAwsRoleCredentials(MongoDbConnection):
    """
    Connect to Mongodb using AWS Role Credentials.
    """
    def get_connection_string(self) -> str:
        current_credentials = get_current_user_or_role_credentials()
        access_key = urllib.parse.quote_plus(current_credentials.access_key)
        secret_key = urllib.parse.quote_plus(current_credentials.secret_key)
        session_token = urllib.parse.quote_plus(current_credentials.token)
        return f"mongodb+srv://{access_key}:{secret_key}@practice.mmdvvxm.mongodb.net/?authSource=%24external&authMechanism=MONGODB-AWS&retryWrites=true" \
                            f"&w=majority&authMechanismProperties=AWS_SESSION_TOKEN:{session_token}"


def connect_to_mongo() -> pymongo.mongo_client:
    """Connect to mongodb with one of the given options.

    Returns:
        pymongo client
    """
    if DATABASE_CLUSTER_DOMAIN == 'localhost':
        connection_string = MongoDbLocalConnection().get_connection_string()
    else:
        connection_string = MongoDbConnectByAwsRoleCredentials().get_connection_string()
    client = pymongo.MongoClient(connection_string)
    return client


def get_database_connection():
    global MONGO_CONNECTION
    if MONGO_CONNECTION is None:
        MONGO_CONNECTION = connect_to_mongo()
    return MONGO_CONNECTION


def get_sync_database_connection():
    global SYNC_MONGO_CONNECTION
    if SYNC_MONGO_CONNECTION is None:
        SYNC_MONGO_CONNECTION = connect_to_mongo()
    return SYNC_MONGO_CONNECTION