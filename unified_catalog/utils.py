from typing import Iterable, Iterator, List, TypeVar

T = TypeVar("T")

def chunked(iterable: Iterable[T], size: int) -> Iterator[List[T]]:
    """Yield lists of up to `size` elements from `iterable`."""
    buf: List[T] = []
    for item in iterable:
        buf.append(item)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf
