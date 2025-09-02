import json, sys, os

def load_seed(path):
    with open(path, 'r') as f:
        data = json.load(f)
    # This is a placeholder; integrate with your models/DB
    print("Loaded seed (preview):")
    print(json.dumps(data, indent=2)[:2000])

if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "seeds/seed.json"
    load_seed(p)
