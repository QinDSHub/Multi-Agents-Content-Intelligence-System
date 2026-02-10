import json, os, hashlib

CACHE_DIR = ".agent_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def cache_key(prefix: str, payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True)
    return f"{prefix}_{hashlib.md5(raw.encode()).hexdigest()}"

def cache_get(key: str):
    path = os.path.join(CACHE_DIR, key + ".json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def cache_set(key: str, value):
    path = os.path.join(CACHE_DIR, key + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

# retry and fallback logic
def safe_invoke(chain, inputs, fallback_chain=None):
    try:
        return chain.invoke(inputs)
    except Exception as e:
        print("⚠️ Primary LLM failed:", e)
        if fallback_chain:
            print("🔁 Falling back...")
            return fallback_chain.invoke(inputs)
        raise




