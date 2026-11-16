"""Trace-driven cache simulator supporting mapping and replacement policies."""
from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Iterable

from . import fifo, lru, mapping, random_replacement

_SIZE_RE = re.compile(r"^\s*(\d+)\s*(B|KB|MB)?\s*$", re.IGNORECASE)
_ADDRESS_RE = re.compile(r"(?i)(?:0x[0-9a-f]+|[0-9a-f]+)")


def parse_size(value: str | int) -> int:
    """Convert values such as 8KB, 64B or integer byte counts into bytes."""
    if isinstance(value, int):
        return value
    match = _SIZE_RE.match(str(value))
    if not match:
        raise ValueError(f"Invalid size '{value}'. Use values such as 8KB or 64B.")
    amount = int(match.group(1))
    unit = (match.group(2) or "B").upper()
    return amount * {"B": 1, "KB": 1024, "MB": 1024 * 1024}[unit]


def parse_trace_text(text: str) -> list[int]:
    """Read memory addresses from trace files in text, CSV, Dinero, or Valgrind formats.

    Supported examples:
    - Simple hex/decimal: '0x00001000', '1A2B', '4096'
    - Read/Write annotated: 'R 0x1000', 'W,0x1010', 'READ 0x1000', 'WRITE 0x1010'
    - CSV tables: 'Workload,Access_No,Address,Operation' -> 'Sequential,1,0x00001000,W'
    - Dinero IV format: '0 0x00400000 4' or '0 00400000 4' (0=read, 1=write, 2=fetch)
    - Valgrind lackey: 'I 00400000,4' or 'L 7fff0000,4'
    """
    addresses: list[int] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.split("#", 1)[0].split("//", 1)[0].strip()
        if not line:
            continue

        lower_line = line.lower()
        # Skip header rows commonly found in CSVs
        if "address" in lower_line or "workload" in lower_line or "access_no" in lower_line:
            continue

        address: int | None = None

        # 1. Look for explicit 0x hex address anywhere in the line
        m_hex = re.search(r"\b0x([0-9a-fA-F]+)\b", line)
        if m_hex:
            try:
                address = int(m_hex.group(1), 16)
            except ValueError:
                address = None

        # 2. If not found, split line by comma or whitespace
        if address is None:
            tokens = [t.strip() for t in re.split(r"[\s,]+", line) if t.strip()]
            if not tokens:
                continue

            # Check for Dinero or Valgrind format: <type> <addr> [<size>]
            # e.g., '0 400000 4', '1 7fff0000', 'I 00400000 4', 'R 1000'
            if len(tokens) >= 2 and tokens[0].upper() in {
                "0", "1", "2", "3", "R", "W", "I", "L", "S", "M", "READ", "WRITE"
            }:
                cand = tokens[1]
                if cand.lower().startswith("0x"):
                    cand = cand[2:]
                if re.fullmatch(r"[0-9a-fA-F]+", cand):
                    try:
                        address = int(cand, 16)
                    except ValueError:
                        pass

            # 3. If still not found, check each token
            if address is None:
                for cand in reversed(tokens):
                    clean_cand = cand[2:] if cand.lower().startswith("0x") else cand
                    if clean_cand.lower() in {
                        "r", "w", "read", "write", "i", "l", "s", "m",
                        "sequential", "loop", "random", "mixed"
                    }:
                        continue
                    if re.fullmatch(r"[0-9a-fA-F]+", clean_cand):
                        try:
                            if re.search(r"[a-fA-F]", clean_cand) or cand.lower().startswith("0x") or len(clean_cand) >= 4:
                                address = int(clean_cand, 16)
                            else:
                                address = int(clean_cand, 10)
                            break
                        except ValueError:
                            continue

        if address is not None:
            addresses.append(address)

    if not addresses:
        raise ValueError("No memory addresses found in the uploaded trace file.")
    return addresses


@dataclass
class CacheConfig:
    cache_size: int
    block_size: int
    associativity: str
    replacement: str

    @classmethod
    def from_dict(cls, config: dict) -> "CacheConfig":
        required = ("cacheSize", "blockSize", "associativity", "replacement")
        missing = [key for key in required if key not in config]
        if missing:
            raise ValueError("Missing configuration field(s): " + ", ".join(missing))
        return cls(
            cache_size=parse_size(config["cacheSize"]),
            block_size=parse_size(config["blockSize"]),
            associativity=str(config["associativity"]),
            replacement=str(config["replacement"]).upper(),
        )


def _ways_from_associativity(value: str, total_lines: int) -> int:
    normalized = value.strip().lower()
    if normalized in {"fully associative", "fully-associative", "fully_associative", "fa"}:
        return total_lines
    match = re.fullmatch(r"(\d+)\s*-?\s*way", normalized)
    if not match:
        raise ValueError(f"Unsupported associativity '{value}'. Use 1-way, 2-way, 4-way, 8-way or Fully Associative.")
    return int(match.group(1))


def simulate(addresses: Iterable[int], config: CacheConfig, hit_time: float = 1.0,
             miss_penalty: float = 50.0, seed: int | None = 0) -> dict:
    """Simulate one configuration and return the frontend API result fields."""
    if config.cache_size <= 0 or config.block_size <= 0:
        raise ValueError("Cache size and block size must be positive.")
    if config.cache_size % config.block_size:
        raise ValueError("Cache size must be exactly divisible by block size.")
    if config.replacement not in {"LRU", "FIFO", "RANDOM"}:
        raise ValueError("Replacement must be LRU, FIFO or Random.")

    total_lines = config.cache_size // config.block_size
    ways = _ways_from_associativity(config.associativity, total_lines)
    if ways <= 0 or ways > total_lines or total_lines % ways:
        raise ValueError("Associativity must be a valid divisor of the number of cache lines.")
    set_count = total_lines // ways

    # Each set stores its resident memory-block numbers. Order is oldest->newest.
    sets: list[list[int]] = [[] for _ in range(set_count)]
    fifo_order: list[list[int]] = [[] for _ in range(set_count)]
    lru_order: list[list[int]] = [[] for _ in range(set_count)]
    rng = random.Random(seed)
    hits = misses = 0

    for address in addresses:
        block_number = int(address) // config.block_size
        set_index = mapping.get_set_index(block_number, set_count)
        current_set = sets[set_index]

        if block_number in current_set:
            hits += 1
            if config.replacement == "LRU":
                order = lru_order[set_index]
                lru.mark_recently_used(order, block_number)
            continue

        misses += 1
        if len(current_set) >= ways:
            if config.replacement == "FIFO":
                victim = fifo.choose_victim(fifo_order[set_index])
                fifo_order[set_index].remove(victim)
            elif config.replacement == "LRU":
                victim = lru.choose_victim(lru_order[set_index])
                lru_order[set_index].remove(victim)
            else:
                victim = random_replacement.choose_victim(current_set, rng)
            current_set.remove(victim)
            if config.replacement == "LRU" and victim in lru_order[set_index]:
                lru_order[set_index].remove(victim)
            if config.replacement == "FIFO" and victim in fifo_order[set_index]:
                fifo_order[set_index].remove(victim)

        current_set.append(block_number)
        if config.replacement == "FIFO":
            fifo_order[set_index].append(block_number)
        elif config.replacement == "LRU":
            lru_order[set_index].append(block_number)

    accesses = hits + misses
    hit_rate = (hits / accesses * 100) if accesses else 0.0
    miss_rate = (misses / accesses * 100) if accesses else 0.0
    amat = hit_time + (misses / accesses) * miss_penalty if accesses else hit_time
    return {
        "accesses": accesses,
        "hits": hits,
        "misses": misses,
        "hitRate": round(hit_rate, 2),
        "missRate": round(miss_rate, 2),
        "amat": round(amat, 2),
    }


def simulate_config(addresses: list[int], raw_config: dict, hit_time: float,
                    miss_penalty: float, workload: str, seed: int | None = 0) -> dict:
    config = CacheConfig.from_dict(raw_config)
    result = simulate(addresses, config, hit_time, miss_penalty, seed)
    return {
        "workload": workload,
        "cacheSize": raw_config["cacheSize"],
        "blockSize": raw_config["blockSize"],
        "associativity": raw_config["associativity"],
        "replacement": raw_config["replacement"],
        **result,
    }
