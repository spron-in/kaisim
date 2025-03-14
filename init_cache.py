
from models import db, APICache
import uuid
import json

def init_predefined_cache():
    """Initialize predefined cache entries"""
    predefined_entries = [
        {
            "api_path": "/api",
            "response": json.dumps({
                  "kind": "APIVersions",
                  "versions": [
                    "v1"
                  ],
                  "serverAddressByClientCIDRs": [
                    {
                      "clientCIDR": "0.0.0.0/0",
                      "serverAddress": "10.128.0.85:443"
                    }
                  ]
            })
        },
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
