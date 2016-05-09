class RepositoryBase(object):
    """
        Expose a public interface with high-level and normalized
        functionalities to communicate with the repository backend.

        When handling content to store in the repository, the implementation
        must always return or expect a stream like object.
    """

    def get(self, path, reference, default=None):
        """Get the content at the reference.

            Args:
                path (str): The content target path.
                reference (str): The commit reference.
                default: The default values to return, None by default.
            Returns:
                IO: The content.
            Raises:
                KeyError if the reference doesn't exists.
        """
        raise NotImplementedError

    def commit(self, index, message=None, author=None, committer=None,
               at_time=None):
        """Commit the index in the repository

            Args:
                index (multiple.repositories.IndexBase):
                    The index to commit.
                message (str): Description of the changes.
                author (str): The commit author, e.g the entity owning the
                    change.
                committer (str): The committer, e.g the entity making the
                    commit.
                at_time (time.struct_time): The time of the commit, if not
                    provided the current UTC time.

            Returns:
                str: The commit reference.

        """
        raise NotImplementedError

    def open_index_at(self, reference):
        """
            Open a new working index at the specified reference

            Args:
                reference (str): The commit reference where to start the, if
                    the reference is equal to None an empty index is created.

            Returns:
                (multiple.repositories.IndexBase)
        """
        raise NotImplementedError

    def walk(**kwargs):
        """
            Walk accross the references

            Args:
                @todo

            Returns:
                (Iterable[str]) The references as string
        """
        raise NotImplementedError


class IndexBase(object):
    """
        The index is the public interface to add or update any stored object.

        When handling content to store in the repository, the implementation
        must always return or expect a stream like object.
    """

    def get(self, path, default=None):
        """Get the content at the path as it is on the index.

            Args:
                path (str): The content target path.
                default: The default values to return, None by default.
            Returns:
                IO: The content.
            Raises:
                KeyError if the path doesn't exists.
        """
        raise NotImplementedError

    def remove(self, paths):
        """Remove the paths from the index."""
        raise NotImplementedError

    def add(self, contents):
        """Add contents to the index.

            Args:
                contents (Iterable[IO, str]): The contents
                    with their corresponding paths.
        """
        raise NotImplementedError
