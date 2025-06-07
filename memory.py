import os
import json

MEMORY_DIR = "conversations"

# 🔧 Ensure directory exists
os.makedirs(MEMORY_DIR, exist_ok=True)


def _get_path(session_id):
    """Generate the path to the memory file."""
    return os.path.join(MEMORY_DIR, f"{session_id}.json")


def load_memory(session_id="default"):
    """Load conversation history from file."""
    path = _get_path(session_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_memory(session_id, memory):
    """Save full memory back to file."""
    path = _get_path(session_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)


def append_message(session_id, role, content):
    """Add a message to memory and save it."""
    memory = load_memory(session_id)
    memory.append({"role": role, "content": content})
    save_memory(session_id, memory)


def reset_memory(session_id="default"):
    """Clear memory file (start fresh)."""
    path = _get_path(session_id)
    if os.path.exists(path):
        os.remove(path)
