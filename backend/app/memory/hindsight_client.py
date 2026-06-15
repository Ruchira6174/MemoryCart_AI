"""
hindsight_client.py — Thin helper retained for backwards compatibility.
All logic has been consolidated into hindsight_memory.py.
Import from hindsight_memory instead of this file.
"""
# Re-export the public API from the canonical module
from app.memory.hindsight_memory import save_memory, retrieve_memory  # noqa: F401
