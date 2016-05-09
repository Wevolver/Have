import calendar
import collections
import io
import itertools
import stat
import time

import dulwich
import dulwich.objects

from multiple import repositories
from multiple import utils


class RepositoryGit(repositories.RepositoryBase):

    def __init__(self, dulwich_repository):
        self.backend = dulwich_repository

    def commit(self, index, message=b'', author=None, committer=None,
               at_time=None):
        # @todo time support
        if not committer:
            committer = author

        if not at_time:
            at_time = time.gmtime()

        commit = dulwich.objects.Commit()

        commit.tree = index.root_tree

        commit.author = author
        commit.committer = committer

        commit.commit_time = commit.author_time = calendar.timegm(at_time)
        commit.commit_timezone = commit.author_timezone = at_time.tm_isdst

        commit.message = message

        self.backend.object_store.add_object(commit)

    def open_index_at(self, reference):
        root_tree = None

        if reference:
            commit = self.backend[reference]

            if isinstance(commit, dulwich.objects.Commit):
                root_tree = self.backend[commit.tree]
            else:
                raise ValueError(
                    "bad reference '%r' is not a "
                    "dulwich.objects.Commit" % commit
                )
        else:
            root_tree = dulwich.objects.Tree()

        return MemoryIndex(root_tree, self.backend.object_store)

    def get(self, path, reference, default=None):
        result = default
        commit = self.backend[reference]

        if isinstance(commit, dulwich.objects.Commit):
            tree = self.backend[commit.tree]
            blob_object = tree.lookup_path(path)
            if isinstance(blob_object, dulwich.objects.Blob):
                result = blob_object.data
                if isinstance(result, str):
                    result = io.StringIO(result)

        return result


class MemoryIndex(object):

    def __init__(self, root_tree, object_store):
        """
            Args:
                root_tree (dulwich.objects.Tree):
                    The root tree of the index
                object_store (dulwich.object_store.BaseObjectStore):
                    The object store where to store the objects.
        """
        self.object_store = object_store
        self._objects = dict(self._get_objects(root_tree))

    @property
    def root_tree(self):
        return self._objects[b''].copy()

    @property
    def objects(self):
        return {
            path: obj.copy()
            for path, obj in self._objects.items()
        }

    def _get_objects(self, start_tree):
        """
            Load in memory all the needed objects

            Returns:
                (Dict(Tuple(str, dulwich.objects.ShaFile)))
        """
        contents = self.object_store.iter_tree_contents(start_tree.id, True)

        for entry in contents:
            yield entry.path, self.object_store[entry.sha]

    def _get_or_create_tree(self, path):
        try:
            return self._objects[path]
        except KeyError:
            tree = dulwich.objects.Tree()
            self._objects[path] = tree

            return tree

    def get(self, path, default=None):
        return self._objects.get(path, default)

    def add(self, contents):
        # @todo a true bulk add without considering every file individually
        for content, path in contents:
            blob = dulwich.objects.Blob.from_string(content.read())
            self._add(path, blob)

    def _add(self, path, blob, file_mode=0o100644):
        processed_path = ProcessedPath.from_path(path)

        self.object_store.add_object(blob)
        self._objects[processed_path.rootless_path] = blob

        paths = list(processed_path.intermediate_paths())

        # first update the leaf tree with the blob objects to add
        leaf_path = paths[-1]
        leaf_tree = self._get_or_create_tree(leaf_path)

        leaf_tree.add(processed_path.basename, file_mode,  blob.id)

        self.object_store.add_object(leaf_tree)

        # iterate the other trees from the nearest until the root
        # and update them
        indexed_paths = list(enumerate(reversed(paths)))

        for idx, intermediate_path in indexed_paths:
            if intermediate_path:
                # if intermediate_path == '' it's the root tree
                _, parent_path = indexed_paths[idx + 1]

                parent_tree = self._get_or_create_tree(parent_path)
                child_tree = self._get_or_create_tree(intermediate_path)
                child_idx = processed_path.tokens_n - 1 - idx
                child_name = processed_path.tokens[child_idx]

                parent_tree.add(child_name, stat.S_IFDIR, child_tree.id)

                self.object_store.add_object(child_tree)
                self.object_store.add_object(parent_tree)
            else:
                break


_ProcessedPath = collections.namedtuple(
    '_ProcessedPath',
    (
        'path',     # intial path with a leading /
        'dirname',  # dirname extracted from the path
        'basename',  # basename extracted from the path
        'tokens',   # tokens of the dirname
        'tokens_n'  # number of tokens
    )
)


class ProcessedPath(_ProcessedPath):

    @classmethod
    def from_path(cls, path):
        if not path.startswith(b'/'):
            path = b'/' + path

        dirname, basename = utils.paths.path_split(path)
        dirname_tokens = dirname.split(b'/')
        n_dirname_tokens = len(dirname_tokens)

        return cls(path, dirname, basename, dirname_tokens, n_dirname_tokens)

    def intermediate_paths(self):
        """
            Generate the intermediate paths with the ProcessedPath.tokens
            values.

                b'/data/files/data.json' -> ['', 'data', 'data/files']

            Returns:
                (iter)
        """
        return itertools.accumulate(self.tokens, utils.paths.path_join)

    @property
    def rootless_path(self):
        return self.path[1:]
