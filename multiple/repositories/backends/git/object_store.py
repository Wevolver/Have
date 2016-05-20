import boto3
import dulwich

from dulwich.repo import OBJECTDIR
from dulwich.object_store import PACKDIR

from multiple import utils
from multiple.repositories.backends import git as git_aws


class AwsS3ObjectStoreIterator(dulwich.object_store.ObjectStoreIterator):
    # TODO
    pass


class AwsS3MissingObjectFinder(dulwich.object_store.MissingObjectFinder):
    # TODO
    pass


class AwsS3ObjectStore(dulwich.object_store.PackBasedObjectStore):
    # TODO
