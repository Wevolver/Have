import pytest
import uuid

from multiple.repositories.backends import git as git_aws


def test_rb_mode_fail(aws_s3_bucket):
    """Test that the rb mode fail if the file doesn't exist"""
    with pytest.raises(IOError) as excinfo:
        git_aws.file.AwsS3GitFile(
            'git-file-test-that-must-not-exist', 'rb', 0, aws_s3_bucket
        )

    assert 'no such file' in str(excinfo.value)


def test_rb_content_can_be_read(aws_s3_file, aws_s3_bucket):
    """Test if the content of the file can be read in rb mode"""
    filename = aws_s3_file['filename']
    content = aws_s3_file['content']

    with git_aws.file.AwsS3GitFile(filename, 'rb', 0, aws_s3_bucket) as git_file:  # noqa
        assert git_file.read() == content
        git_file.seek(0)
        assert git_file.read(3) == content[:3]


def test_rb_can_not_be_write(aws_s3_file, aws_s3_bucket):
    """Test that a file cannot be write in rb mode"""
    filename = aws_s3_file['filename']

    with git_aws.file.AwsS3GitFile(filename, 'rb', 0, aws_s3_bucket) as git_file:  # noqa
        with pytest.raises(IOError) as excinfo_write:
            git_file.write(b'0')

        with pytest.raises(IOError) as excinfo_writelines:
            git_file.writelines((b'0', b'0'))

        assert 'read-only file' in str(excinfo_write.value)
        assert 'read-only file' in str(excinfo_writelines.value)
        assert not git_file.is_writable
        assert not git_file.writable()
        assert 'r' in git_file.mode


def test_existing_rw_can_be_write(aws_s3_file, aws_s3_bucket):
    """Test that a file can be write and the content is properly flushed to the
       s3 bucket when it's closed.
    """
    content = b'1' * 20
    filename = aws_s3_file['filename']

    with git_aws.file.AwsS3GitFile(filename, 'wb', 0, aws_s3_bucket) as git_file:  # noqa
        bytes_written = git_file.write(content)

        assert aws_s3_file['content'] != content
        assert bytes_written == len(content)

    with git_aws.file.AwsS3GitFile(filename, 'rb', 0, aws_s3_bucket) as git_file:  # noqa
        assert git_file.read() == content


def test_new_wb_can_be_write(aws_s3_bucket, unique_filename):
    """Test that when a non existing file is open in wb mode the file is
       created and the content written can be read afterwards.
    """
    content = b'1' * 20

    with git_aws.file.AwsS3GitFile(unique_filename, 'wb', 0, aws_s3_bucket) as git_file:  # noqa
        bytes_written = git_file.write(content)

        assert bytes_written == len(content)

    with git_aws.file.AwsS3GitFile(unique_filename, 'rb', 0, aws_s3_bucket) as git_file:  # noqa
        assert git_file.read() == content


def test_wb_lock(aws_s3_bucket, unique_filename):
    """Test that a file in wb is locked and cannot be opened twice (or more)"""
    with git_aws.file.AwsS3GitFile(unique_filename, 'wb', 0, aws_s3_bucket) as git_file:  # noqa
        with pytest.raises(IOError) as excinfo:
            # must fail
            git_aws.file.AwsS3GitFile(unique_filename, 'wb', 0, aws_s3_bucket)


def test_rb_not_locked(aws_s3_file, aws_s3_bucket):
    """Test that file open in rb mode can be opened twice (or more)"""
    filename = aws_s3_file['filename']

    with git_aws.file.AwsS3GitFile(filename, 'rb', 0, aws_s3_bucket) as git_file_a:  # noqa
        with git_aws.file.AwsS3GitFile(filename, 'rb', 0, aws_s3_bucket) as git_file_b:  # noqa
            assert git_file_a.read() == git_file_b.read()


@pytest.mark.parametrize(
    'mode,expected_message',
    (('r', 'text mode not supported'),
     ('ab', 'append mode not supported'),
     ('r+b', 'read/write mode not supported'),
     ('w+b', 'read/write mode not supported'),
     ('a+bU', 'append mode not supported'), )
)
def test_invalid_mode(aws_s3_bucket, mode, expected_message):
    """Test that the non supported mode throw an exception"""
    filename = 'git-file-test'

    with pytest.raises(IOError) as excinfo:
        git_aws.file.AwsS3GitFile(filename, mode, 0, aws_s3_bucket)

    assert expected_message in str(excinfo.value)
