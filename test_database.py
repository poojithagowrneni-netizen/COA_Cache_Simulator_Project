import unittest
from database import (
    check_connection,
    clear_all_simulation_runs,
    delete_simulation_run,
    get_all_simulation_runs,
    get_simulation_run,
    save_simulation_run,
)


class DatabaseTests(unittest.TestCase):
    def test_database_connection(self):
        status = check_connection()
        self.assertIsInstance(status, dict)
        self.assertTrue(status.get("connected"), f"MongoDB failed to connect: {status.get('error')}")
        self.assertIn("localhost:27017", status.get("uri"))
        self.assertIsNotNone(status.get("version"))

    def test_save_and_retrieve_run(self):
        sample_results = [
            {
                "workload": "test.trace",
                "cacheSize": "16KB",
                "blockSize": "64B",
                "associativity": "2-way",
                "replacement": "LRU",
                "accesses": 100,
                "hits": 80,
                "misses": 20,
                "hitRate": 80.0,
                "missRate": 20.0,
                "amat": 11.0,
            }
        ]
        run_id = save_simulation_run(
            workload="test.trace",
            configs_count=1,
            best="16KB / 64B / 2-way / LRU",
            results=sample_results,
            hit_time=1.0,
            miss_penalty=50.0,
        )
        self.assertIsNotNone(run_id)

        # Retrieve single run
        run = get_simulation_run(run_id)
        self.assertIsNotNone(run)
        self.assertEqual(run["workload"], "test.trace")
        self.assertEqual(run["count"], 1)
        self.assertEqual(len(run["results"]), 1)

        # Clean up this specific run
        deleted = delete_simulation_run(run_id)
        self.assertTrue(deleted)
        self.assertIsNone(get_simulation_run(run_id))


if __name__ == "__main__":
    unittest.main()
