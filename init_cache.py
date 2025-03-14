
from app import app
from models import db, APICache
import uuid
import json

def init_predefined_cache():
    """Initialize predefined cache entries from JSON file"""
    try:
        with open('predefined_cache.json', 'r') as f:
            config = json.load(f)
            predefined_entries = [{
                "api_path": entry["api_path"],
                "response": json.dumps(entry["response"])
            } for entry in config["entries"]]

        with app.app_context():
            for entry in predefined_entries:
                # Check if entry already exists
                existing = APICache.query.filter_by(
                    api_path=entry["api_path"],
                    is_predefined=True
                ).first()
                
                if not existing:
                    cache_entry = APICache(
                        cache_id=uuid.uuid4(),
                        api_path=entry["api_path"],
                        response=entry["response"],
                        is_predefined=True
                    )
                    db.session.add(cache_entry)
            
            db.session.commit()
            print("Predefined cache entries initialized successfully")

    except FileNotFoundError:
        print("Warning: predefined_cache.json not found")
    except json.JSONDecodeError:
        print("Error: Invalid JSON in predefined_cache.json")
    except Exception as e:
        print(f"Error initializing cache: {str(e)}")

if __name__ == "__main__":
    init_predefined_cache()
