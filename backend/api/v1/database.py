import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from api.v1.models import (
    UserDoc,
    SimulationDoc,
    QuestDoc,
    LibraryResourceDoc,
    SkillNodeDoc,
    AnalyticsEventDoc
)

# Global flag to indicate database state
_db_mode = "mock"
_db_ref = None

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json")
    if os.path.exists(cred_path):
        # Prevent double initialization
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            bucket = os.getenv("FIREBASE_STORAGE_BUCKET")
            firebase_admin.initialize_app(cred, {
                "storageBucket": bucket
            })
        _db_ref = firestore.client()
        _db_mode = "firestore"
        print(f"[Database] Firebase Firestore initialized successfully from: {cred_path}")
    else:
        print(f"[Database] Firebase credentials not found at '{cred_path}'. Operating in local fallback JSON mode.")
except Exception as e:
    print(f"[Database] Failed to initialize Firebase Admin SDK: {e}. Operating in local fallback JSON mode.")

MOCK_DB_FILE = "./alterlife_db.json"

def _load_mock_db() -> Dict[str, Any]:
    if not os.path.exists(MOCK_DB_FILE):
        return {"users": {}, "simulations": {}, "quests": {}, "library": {}, "skills": {}, "analytics": {}}
    try:
        with open(MOCK_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"users": {}, "simulations": {}, "quests": {}, "library": {}, "skills": {}, "analytics": {}}

def _save_mock_db(db_data: Dict[str, Any]) -> None:
    try:
        with open(MOCK_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Database] Error writing to local DB: {e}")

# ── API Interface ─────────────────────────────────────────────────────────────

def get_db_mode() -> str:
    return _db_mode

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    if _db_mode == "firestore" and _db_ref:
        doc = _db_ref.collection("users").document(user_id).get()
        return doc.to_dict() if doc.exists else None
    else:
        db = _load_mock_db()
        return db.get("users", {}).get(user_id)

def save_user(user_id: str, data: Dict[str, Any]) -> None:
    existing = get_user(user_id) or {"userId": user_id, "email": data.get("email", f"{user_id}@placeholder.com")}
    merged = {**existing, **data}
    merged["updatedAt"] = datetime.utcnow().isoformat() + "Z"
    
    validated = UserDoc(**merged).model_dump()
    
    if _db_mode == "firestore" and _db_ref:
        _db_ref.collection("users").document(user_id).set(validated, merge=True)
    else:
        db = _load_mock_db()
        if "users" not in db: db["users"] = {}
        db["users"][user_id] = validated
        _save_mock_db(db)

def get_simulation_tree(simulation_id: str) -> Optional[Dict[str, Any]]:
    if _db_mode == "firestore" and _db_ref:
        doc = _db_ref.collection("simulations").document(simulation_id).get()
        return doc.to_dict() if doc.exists else None
    else:
        db = _load_mock_db()
        return db.get("simulations", {}).get(simulation_id)

def save_simulation_tree(simulation_id: str, data: Dict[str, Any]) -> None:
    # Ensure it's valid according to model
    validated = SimulationDoc(**data).model_dump()
    if _db_mode == "firestore" and _db_ref:
        _db_ref.collection("simulations").document(simulation_id).set(validated)
    else:
        db = _load_mock_db()
        if "simulations" not in db: db["simulations"] = {}
        db["simulations"][simulation_id] = validated
        _save_mock_db(db)

def get_daily_quests(user_id: str) -> List[Dict[str, Any]]:
    if _db_mode == "firestore" and _db_ref:
        docs = _db_ref.collection("quests").document(user_id).get()
        if docs.exists:
            return docs.to_dict().get("quests", [])
        return []
    else:
        db = _load_mock_db()
        return db.get("quests", {}).get(user_id, [])

def save_daily_quests(user_id: str, quests: List[Dict[str, Any]]) -> None:
    validated_quests = [QuestDoc(**q).model_dump() for q in quests]
    if _db_mode == "firestore" and _db_ref:
        _db_ref.collection("quests").document(user_id).set({"quests": validated_quests})
    else:
        db = _load_mock_db()
        if "quests" not in db: db["quests"] = {}
        db["quests"][user_id] = validated_quests
        _save_mock_db(db)

# ── Library ───────────────────────────────────────────────────────────────────

def get_library(user_id: str) -> List[Dict[str, Any]]:
    if _db_mode == "firestore" and _db_ref:
        docs = _db_ref.collection("library").document(user_id).get()
        if docs.exists:
            return docs.to_dict().get("resources", [])
        return []
    else:
        db = _load_mock_db()
        return db.get("library", {}).get(user_id, [])

def save_library(user_id: str, resources: List[Dict[str, Any]]) -> None:
    validated_resources = [LibraryResourceDoc(**r).model_dump() for r in resources]
    if _db_mode == "firestore" and _db_ref:
        _db_ref.collection("library").document(user_id).set({"resources": validated_resources})
    else:
        db = _load_mock_db()
        if "library" not in db: db["library"] = {}
        db["library"][user_id] = validated_resources
        _save_mock_db(db)

# ── Skills ────────────────────────────────────────────────────────────────────

def get_skills(user_id: str) -> List[Dict[str, Any]]:
    if _db_mode == "firestore" and _db_ref:
        docs = _db_ref.collection("skills").document(user_id).get()
        if docs.exists:
            return docs.to_dict().get("nodes", [])
        return []
    else:
        db = _load_mock_db()
        return db.get("skills", {}).get(user_id, [])

def save_skills(user_id: str, nodes: List[Dict[str, Any]]) -> None:
    validated_nodes = [SkillNodeDoc(**n).model_dump() for n in nodes]
    if _db_mode == "firestore" and _db_ref:
        _db_ref.collection("skills").document(user_id).set({"nodes": validated_nodes})
    else:
        db = _load_mock_db()
        if "skills" not in db: db["skills"] = {}
        db["skills"][user_id] = validated_nodes
        _save_mock_db(db)

# ── Analytics ─────────────────────────────────────────────────────────────────

def get_analytics_events(user_id: str) -> List[Dict[str, Any]]:
    if _db_mode == "firestore" and _db_ref:
        docs = _db_ref.collection("analytics").document(user_id).get()
        if docs.exists:
            return docs.to_dict().get("events", [])
        return []
    else:
        db = _load_mock_db()
        return db.get("analytics", {}).get(user_id, [])

def append_analytics_event(user_id: str, event: Dict[str, Any]) -> None:
    validated_event = AnalyticsEventDoc(**event).model_dump()
    events = get_analytics_events(user_id)
    events.append(validated_event)
    
    if _db_mode == "firestore" and _db_ref:
        _db_ref.collection("analytics").document(user_id).set({"events": events})
    else:
        db = _load_mock_db()
        if "analytics" not in db: db["analytics"] = {}
        db["analytics"][user_id] = events
        _save_mock_db(db)
