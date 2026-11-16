"""FIFO replacement: evict the block that entered its set earliest."""

def choose_victim(insertion_order: list[int]) -> int:
    if not insertion_order:
        raise ValueError("Cannot evict from an empty cache set.")
    return insertion_order[0]
