"""LRU replacement: evict the block accessed least recently."""

def choose_victim(recency_order: list[int]) -> int:
    if not recency_order:
        raise ValueError("Cannot evict from an empty cache set.")
    return recency_order[0]


def mark_recently_used(recency_order: list[int], block_number: int) -> None:
    if block_number in recency_order:
        recency_order.remove(block_number)
    recency_order.append(block_number)
