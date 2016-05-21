import botocore
import io


class AwsS3GitFile(object):
    """File in a s3 bucket that follows the git locking protocol for writes.


    Note:
        You *must* call close() or abort() on a _GitFile for the lock to be
        released. Typically this will happen in a finally block.

    Todo:
        Implement the lock; using SimpleDB, a Redis lock or just writting a
        lock file on the bucket?
    """

    PROXY_METHODS = {
        '__iter__', 'fileno', 'isatty', 'read',
        'readline', 'readlines', 'seek', 'tell',
        'truncate',
    }

    def __init__(self, filename, mode, bufsize, aws_s3_bucket):
        """
            Args:
                filename (str):
                    The filename, the full key of the file in the s3 bucket.
                mode (str):
                    The mode of the file, only read/write in binary mode is
                    currently supported.
                bufsize (int):
                    The size of the buffer, currently ignored.
                aws_s3_bucket (s3.Bucket):
                    The bucket used to store the file.
            Raises:
                IOError: If the mode isn't supported
        """
        self.is_supported_mode(mode, raise_exception=True)

        self._aws_bucket = aws_s3_bucket
        self._aws_key = None

        self._filename = filename
        self._lock_name = None

        self._mode = mode
        self._mode_set = set(self._mode)

        self._is_writable = None

        self._buffer = None
        try:
            s3_object = self.aws_key.get()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey' and self.is_writable:
                self._buffer = io.BytesIO()
            else:
                raise
        else:
            self._buffer = io.BytesIO(s3_object['Body'].read())

        for method in self.PROXY_METHODS:
            setattr(self, method, getattr(self._buffer, method))

        self.errors = None
        self.newlines = None
        self.encoding = None
        self.softspace = None

    def is_supported_mode(self, mode, raise_exception=False):
        """Check if a mode is supported.

            Args:
                mode (str):
                    The mode to check
                raise_exception (bool):
                    Raise an exception if the mode isn't valid
            Returns:
                bool: True if the mode is supported
            Raises:
                IOError: If the mode isn't supported
        """
        supported = False

        if 'a' in mode:
            if raise_exception:
                raise IOError('append mode not supported for Git files')
        elif '+' in mode:
            if raise_exception:
                raise IOError('read/write mode not supported for Git files')
        elif 'b' not in mode:
            if raise_exception:
                raise IOError('text mode not supported for Git files')
        else:
            supported = True

        return supported

    @property
    def closed(self):
        return self._buffer.closed

    @property
    def mode(self):
        return self._mode

    @property
    def name(self):
        return self._filename

    @property
    def aws_key(self):
        if not self._aws_key:
            self._aws_key = self._aws_bucket.Object(self._filename)

        return self._aws_key

    @property
    def is_writable(self):
        if not self._is_writable:
            self._is_writable = self.writable()

        return self._is_writable

    @property
    def lock_name(self):
        if not self._lock_name:
            self._lock_name = '{0}.lock'.format(self._filename)

        return self._lock_name

    def writable(self):
        return bool({'w', '+'} & self._mode_set)

    def write(self, *args, **kwarg):
        if self.is_writable:
            return self._buffer.write(*args, **kwarg)

        raise IOError('read-only file')

    def writelines(self, *args, **kwarg):
        if self.is_writable:
            return self._buffer.writelines(*args, **kwarg)

        raise IOError('read-only file')

    def abort(self):
        self.close()

    def flush(self):
        self._buffer.flush()
        if self.is_writable:
            self.seek(0)
            self.aws_key.put(Body=self._buffer)

    def close(self):
        self._buffer.close()

    def aquire_lock(self):
        # TODO
        pass

    def release_lock(self):
        # TODO
        pass

    def __enter__(self):
        if self.is_writable:
            self.aquire_lock()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()
        self.close()

        if self.is_writable:
            self.release_lock()
