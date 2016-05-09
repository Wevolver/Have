def path_join(*args):
    """
        Join a /-delimited path.

    """
    return b'/'.join([p for p in args if p])


def path_split(path):
    """
        Split a /-delimited path into a directory part and a basename.

        Args:
            path (bytes): The path to split.

        Returns:
            (tuple(bytes, bytes)) Tuple with directory name and basename
    """
    try:
        (dirname, basename) = path.rsplit(b'/', 1)
    except ValueError:
        return (b'', path)
    else:
        return (dirname, basename)
