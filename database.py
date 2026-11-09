"""MongoDB database connection and persistence layer for COA Cache Simulator."""
from datetime import datetime, timezone
import logging
import os
from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)

# Configurable MongoDB URI and Database Name
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "cache_simulator")

_client = None


def get_client() -> MongoClient:
    """Get or initialize singleton MongoClient."""
    global _client
    if _client is None:
        _client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=2000,
            connectTimeoutMS=2000,
        )
    return _client


def get_db():
    """Get MongoDB database instance."""
    client = get_client()
    return client[MONGO_DB_NAME]


def check_connection() -> dict:
    """Test connection to MongoDB server and return status."""
    try:
        client = get_client()
        # Ping the admin database to verify active connection
        info = client.admin.command("ping")
        server_info = client.server_info()
        return {
            "connected": bool(info.get("ok")),
            "uri": MONGO_URI,
            "database": MONGO_DB_NAME,
            "version": server_info.get("version", "unknown"),
            "error": None,
        }
    except Exception as exc:
        logger.warning(f"MongoDB connection check failed: {exc}")
        return {
            "connected": False,
            "uri": MONGO_URI,
            "database": MONGO_DB_NAME,
            "version": None,
            "error": str(exc),
        }


def save_simulation_run(
    workload: str,
    configs_count: int,
    best: str,
    results: list,
    hit_time: float = 1.0,
    miss_penalty: float = 50.0,
) -> str | None:
    """Persist a simulation run with results to MongoDB."""
    try:
        db = get_db()
        now = datetime.now(timezone.utc)
        document = {
            "workload": workload,
            "count": configs_count,
            "best": best,
            "results": results,
            "hitTime": hit_time,
            "missPenalty": miss_penalty,
            "createdAt": now.isoformat(),
            "date": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        }
        res = db["simulations"].insert_one(document)
        return str(res.inserted_id)
    except PyMongoError as exc:
        logger.error(f"Failed to save simulation to MongoDB: {exc}")
        return None


def get_all_simulation_runs(limit: int = 100) -> list:
    """Retrieve past simulation runs sorted newest first."""
    try:
        db = get_db()
        cursor = db["simulations"].find().sort("_id", -1).limit(limit)
        runs = []
        for doc in cursor:
            runs.append({
                "id": str(doc["_id"]),
                "workload": doc.get("workload", "unknown"),
                "count": doc.get("count", 0),
                "best": doc.get("best", "N/A"),
                "date": doc.get("date", ""),
                "createdAt": doc.get("createdAt", ""),
                "hitTime": doc.get("hitTime", 1),
                "missPenalty": doc.get("missPenalty", 50),
                "results": doc.get("results", []),
            })
        return runs
    except PyMongoError as exc:
        logger.error(f"Failed to fetch simulation runs from MongoDB: {exc}")
        return []


def get_simulation_run(run_id: str) -> dict | None:
    """Retrieve a single simulation run by ID."""
    try:
        db = get_db()
        obj_id = ObjectId(run_id) if ObjectId.is_valid(run_id) else run_id
        doc = db["simulations"].find_one({"_id": obj_id})
        if not doc:
            return None
        return {
            "id": str(doc["_id"]),
            "workload": doc.get("workload", "unknown"),
            "count": doc.get("count", 0),
            "best": doc.get("best", "N/A"),
            "date": doc.get("date", ""),
            "createdAt": doc.get("createdAt", ""),
            "hitTime": doc.get("hitTime", 1),
            "missPenalty": doc.get("missPenalty", 50),
            "results": doc.get("results", []),
        }
    except PyMongoError as exc:
        logger.error(f"Failed to fetch simulation {run_id} from MongoDB: {exc}")
        return None


def delete_simulation_run(run_id: str) -> bool:
    """Delete a simulation run by ID."""
    try:
        db = get_db()
        obj_id = ObjectId(run_id) if ObjectId.is_valid(run_id) else run_id
        res = db["simulations"].delete_one({"_id": obj_id})
        return res.deleted_count > 0
    except PyMongoError as exc:
        logger.error(f"Failed to delete simulation {run_id} from MongoDB: {exc}")
        return False


def clear_all_simulation_runs() -> int:
    """Delete all simulation runs from MongoDB."""
    try:
        db = get_db()
        res = db["simulations"].delete_many({})
        return res.deleted_count
    except PyMongoError as exc:
        logger.error(f"Failed to clear simulations from MongoDB: {exc}")
        return 0
