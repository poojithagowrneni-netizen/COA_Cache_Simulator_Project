import unittest
from cache.simulator import CacheConfig, parse_trace_text, simulate


class CacheSimulatorTests(unittest.TestCase):
    def test_trace_parser(self):
        self.assertEqual(parse_trace_text("0x0\n0x4\nR 0x0\n"), [0, 4, 0])

    def test_trace_parser_csv_and_dinero(self):
        csv_text = "Workload,Access_No,Address,Operation\nSequential,1,0x00001000,W\nSequential,2,0x00001010,R\n"
        self.assertEqual(parse_trace_text(csv_text), [0x1000, 0x1010])

        dinero_text = "0 0x1000 4\n1 0x1010 4\n"
        self.assertEqual(parse_trace_text(dinero_text), [0x1000, 0x1010])

        valgrind_text = "I 00400000,4\nL 00400010,4\n"
        self.assertEqual(parse_trace_text(valgrind_text), [0x400000, 0x400010])

    def test_fifo_hit_and_miss(self):
        cfg = CacheConfig( cache_size=2, block_size=1, associativity="2-way", replacement="FIFO")
        result = simulate([0, 1, 0, 2, 1], cfg)
        self.assertEqual((result["hits"], result["misses"]), (2, 3))

    def test_lru_replacement(self):
        cfg = CacheConfig(cache_size=2, block_size=1, associativity="2-way", replacement="LRU")
        result = simulate([0, 1, 0, 2, 0], cfg)
        self.assertEqual((result["hits"], result["misses"]), (2, 3))

    def test_direct_mapping_conflict(self):
        cfg = CacheConfig(cache_size=2, block_size=1, associativity="1-way", replacement="LRU")
        result = simulate([0, 2, 0], cfg)
        self.assertEqual((result["hits"], result["misses"]), (0, 3))

    def test_random_is_reproducible_with_seed(self):
        cfg = CacheConfig(cache_size=2, block_size=1, associativity="2-way", replacement="RANDOM")
        self.assertEqual(simulate([0, 1, 2, 0, 1], cfg), simulate([0, 1, 2, 0, 1], cfg))


if __name__ == "__main__":
    unittest.main()
