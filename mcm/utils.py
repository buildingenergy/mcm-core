from itertools import islice, chain

def batch(iterable, size):
    """Generator to return iterators of size ``size``.

    :param iterable: any iterable type, items you need batched up.
    :param size: int, batch size.
    :rtype: iterable or lists.

    """
    sourceiter = iter(iterable)
    while 1:
        batchiter = islice(sourceiter, size)
        yield list(chain([batchiter.next()], batchiter))

