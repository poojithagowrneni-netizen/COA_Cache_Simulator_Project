"""Random replacement: evict a randomly selected resident cache block."""
import random


def choose_victim(resident_blocks: list[int], rng: random.Random) -> int:
    if not resident_blocks:
        raise ValueError("Cannot evict from an empty cache set.")
    return rng.choice(resident_blocks)
