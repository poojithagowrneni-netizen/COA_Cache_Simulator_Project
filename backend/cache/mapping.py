"""Cache placement calculations for direct and set-associative mapping."""

def get_set_index(block_number: int, number_of_sets: int) -> int:
    """Return the only set in which a memory block is allowed to reside."""
    if number_of_sets <= 0:
        raise ValueError("Number of cache sets must be positive.")
    return block_number % number_of_sets


def get_tag(block_number: int, number_of_sets: int) -> int:
    """Return the tag portion of a block number for the selected set."""
    if number_of_sets <= 0:
        raise ValueError("Number of cache sets must be positive.")
    return block_number // number_of_sets
