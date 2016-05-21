import dulwich

from multiple.repositories.backends import git as git_aws


def load_pack_index(path, aws_s3_bucket):
    """Load an index file by bucket key.

        Args:
            path (str):
                The key to the index file in the aws s3 bucket.
            aws_s3_bucket (boto3.Bucket):
                The aws s3 bucket where the file pack index is stored.
        Returns:
            PackIndex: Loaded pack index file
    """
    with git_aws.file.AwsS3GitFile(
        path, 'rb', 0, aws_s3_bucket=aws_s3_bucket
    ) as f:
        return dulwich.pack.load_pack_index_file(path, f)


class AwsS3PackData(dulwich.pack.PackData):
    PACK_HEADER_SIZE = 12
    """
        Pack header:
             4-byte signature:
                 The signature is: {'P', 'A', 'C', 'K'}

             4-byte version number (network byte order):
             Git currently accepts version number 2 or 3 but
                 generates version 2 only.

             4-byte number of objects contained in the pack (network byte
            order)
    """
    OFFSET_CACHE_SIZE = 1024 * 1024 * 20

    def __init__(self, filename, aws_s3_bucket, file=None):
        """
            Args:
                filename (str):
                    The full key of the pack file in the aws s3 bucket.
                aws_s3_bucket (s3.Bucket):
                    The aws s3 bucket where the file pack is stored.
        """
        self._aws_bucket = aws_s3_bucket
        self._filename = filename
        self._header_size = self.PACK_HEADER_SIZE

        if not isinstance(git_aws.file.AwsS3GitFile, file):
            raise ValueError('unsupported file interface %r', file)

        if file is None:
            self._file = git_aws.file.AwsS3GitFile(
                self._filename, 'rb', 0, aws_s3_bucket=self._aws_bucket
            )

        self._offset_cache = dulwich.lru_cache.LRUSizeCache(
            self.OFFSET_CACHE_SIZE,
            compute_size=dulwich.lru_cache._compute_object_size
        )

        self.pack = None


class AwsS3Pack(dulwich.pack.Pack):
    """A Git pack object implemented in a amazon s3 bucket."""

    def __init__(self, *args, **kwargs):
        self._aws_bucket = kwargs.pop('aws_s3_bucket')

        super().__init__(*args, **kwargs)

        self._data_load = lambda: AwsS3PackData(
            self._data_path, self.aws_bucket
        )

        self._idx_load = lambda: load_pack_index(
            self._idx_path, self._aws_bucket
        )
