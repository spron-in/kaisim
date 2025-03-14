
from models import db, APICache
import uuid
import json

def init_predefined_cache():
    """Initialize predefined cache entries"""
    predefined_entries = [
        {
            "api_path": "/api/v1/namespaces/default/pods",
            "response": json.dumps({
                "kind": "PodList",
                "apiVersion": "v1",
                "items": [
                    {
                        "metadata": {
                            "name": "example-pod",
                            "namespace": "default"
                        },
                        "status": {
                            "phase": "Running"
                        }
                    }
                ]
            })
        },
        {
            "api_path": "/api/v1/namespaces/default/services",
            "response": json.dumps({
                "kind": "ServiceList",
                "apiVersion": "v1",
                "items": []
            })
        }
    ]

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

if __name__ == "__main__":
    init_predefined_cache()
    print("Predefined cache entries initialized successfully")
