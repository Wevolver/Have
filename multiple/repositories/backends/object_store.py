import boto3
import dulwich


class AwsS3ObjectStore(dulwich.object_store.BaseObjectStore):


    def __init__(self, aws_access_key_id, aws_secret_access_key,
                 aws_session_token):
        super().__init__()


