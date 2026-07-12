import os
import json
import sys

# Ensure backend directory is in path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.v1.database import _db_mode, _db_ref
from api.v1.models import (
    UserDoc,
    SimulationDoc,
    QuestDoc,
    LibraryResourceDoc,
    SkillNodeDoc,
    AnalyticsEventDoc
)

MOCK_DB_FILE = "../alterlife_db.json"

def migrate():
    if _db_mode != "firestore" or not _db_ref:
        print("❌ Firestore is not initialized. Please ensure FIREBASE_CREDENTIALS_PATH is correct and valid.")
        return

    db_path = os.path.join(os.path.dirname(__file__), MOCK_DB_FILE)
    if not os.path.exists(db_path):
        print(f"❌ Mock DB file not found at {db_path}")
        return

    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("🚀 Starting Migration to Firestore...")
    batch = _db_ref.batch()
    operations_count = 0

    def commit_batch():
        nonlocal batch, operations_count
        if operations_count > 0:
            batch.commit()
            print(f"✅ Committed batch of {operations_count} operations.")
            batch = _db_ref.batch()
            operations_count = 0

    # 1. Users
    users = data.get("users", {})
    for user_id, user_data in users.items():
        try:
            # fill missing defaults if necessary
            if "email" not in user_data:
                user_data["email"] = f"{user_id}@placeholder.com"
            if "userId" not in user_data:
                user_data["userId"] = user_id
                
            validated = UserDoc(**user_data).model_dump()
            doc_ref = _db_ref.collection("users").document(user_id)
            batch.set(doc_ref, validated, merge=True)
            operations_count += 1
            if operations_count >= 400: commit_batch()
        except Exception as e:
            print(f"⚠️ Error migrating user {user_id}: {e}")

    # 2. Simulations
    simulations = data.get("simulations", {})
    for sim_id, sim_data in simulations.items():
        try:
            validated = SimulationDoc(**sim_data).model_dump()
            doc_ref = _db_ref.collection("simulations").document(sim_id)
            batch.set(doc_ref, validated)
            operations_count += 1
            if operations_count >= 400: commit_batch()
        except Exception as e:
            print(f"⚠️ Error migrating simulation {sim_id}: {e}")

    # 3. Quests
    quests = data.get("quests", {})
    for user_id, quest_list in quests.items():
        try:
            validated_list = [QuestDoc(**q).model_dump() for q in quest_list]
            doc_ref = _db_ref.collection("quests").document(user_id)
            batch.set(doc_ref, {"quests": validated_list})
            operations_count += 1
            if operations_count >= 400: commit_batch()
        except Exception as e:
            print(f"⚠️ Error migrating quests for user {user_id}: {e}")

    # 4. Library
    library = data.get("library", {})
    for user_id, lib_list in library.items():
        try:
            validated_list = [LibraryResourceDoc(**r).model_dump() for r in lib_list]
            doc_ref = _db_ref.collection("library").document(user_id)
            batch.set(doc_ref, {"resources": validated_list})
            operations_count += 1
            if operations_count >= 400: commit_batch()
        except Exception as e:
            print(f"⚠️ Error migrating library for user {user_id}: {e}")

    # 5. Skills
    skills = data.get("skills", {})
    for user_id, skill_list in skills.items():
        try:
            validated_list = [SkillNodeDoc(**s).model_dump() for s in skill_list]
            doc_ref = _db_ref.collection("skills").document(user_id)
            batch.set(doc_ref, {"nodes": validated_list})
            operations_count += 1
            if operations_count >= 400: commit_batch()
        except Exception as e:
            print(f"⚠️ Error migrating skills for user {user_id}: {e}")

    # 6. Analytics
    analytics = data.get("analytics", {})
    for user_id, event_list in analytics.items():
        try:
            validated_list = [AnalyticsEventDoc(**e).model_dump() for e in event_list]
            doc_ref = _db_ref.collection("analytics").document(user_id)
            batch.set(doc_ref, {"events": validated_list})
            operations_count += 1
            if operations_count >= 400: commit_batch()
        except Exception as e:
            print(f"⚠️ Error migrating analytics for user {user_id}: {e}")

    commit_batch()
    print("🎉 Migration completed successfully!")

if __name__ == "__main__":
    migrate()
