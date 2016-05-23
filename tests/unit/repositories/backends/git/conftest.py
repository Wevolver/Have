import boto3
import os
import placebo
import pytest
import uuid


@pytest.fixture()
def unique_filename():
    return 'test-file-{uuid!s}'.format(uuid=uuid.uuid4())


@pytest.fixture(scope='session')
def aws_s3_bucket(aws_session):
    """Provide an aws s3 bucket.

        Note:
            This method require to have set the environment variable:
                - MULTIPLE_TEST_AWS_S3_BUCKET : The name of the bucket to use
                    for the tests.
    """
    try:
        bucket_name = os.environ['MULTIPLE_TEST_AWS_S3_BUCKET']
    except KeyError:
        raise ValueError("MULTIPLE_TEST_AWS_S3_BUCKET isn't set")

    s3 = aws_session.resource('s3')
    bucket = s3.Bucket(bucket_name)

    bucket.objects.delete()

    return bucket


@pytest.fixture()
def aws_s3_file(aws_s3_bucket, unique_filename):
    content = b'0' * 20

    s3_file = aws_s3_bucket.Object(unique_filename).put(Body=content)

    return {
        's3_file': s3_file,
        'content': content,
        'filename': unique_filename
    }


@pytest.fixture(scope='session')
def aws_session():
    """Provide an aws session.

        Note:
            Inspired from the placebo.utils.placebo_session decoractor.

            Like the placebo_session decoractor some environment variables
            can be set:
                - MULTIPLE_TEST_PLACEBO_MODE : to switch the placebo mode,
                    either 'record', 'playback', or 'off', 'playback' is
                    thedefault. In 'off' mode placebo isn't used.
    """
    session = boto3.Session()

    mode = os.environ.get('MULTIPLE_TEST_PLACEBO_MODE', 'playback')

    if mode not in ('off', 'record', 'playback'):
        raise ValueError('unknow placebo mode %r', mode)

    if mode != 'off':
        directory_name = os.path.dirname(os.path.realpath(__file__))
        record_directory = os.path.join(directory_name, 'aws-data', 'records')

        if not os.path.exists(record_directory):
            os.makedirs(record_directory)

        pill = placebo.attach(session, data_path=record_directory)

        if mode == 'record':
            pill.record()
        elif mode == 'playback':
            pill.playback()

    return session
