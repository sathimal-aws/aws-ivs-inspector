import sys, json;
from dotenv import set_key
from pathlib import Path

existing_env_vars = json.loads(sys.argv[1])

env_file_path = Path("./.env")
env_file_path.touch(mode=0o600, exist_ok=False)

if len(existing_env_vars):
    for k,v in existing_env_vars.items():
        if not k.startswith("VITE_"):
            set_key(dotenv_path=env_file_path, key_to_set=f"VITE_{k}", value_to_set=v)
        else:
            set_key(dotenv_path=env_file_path, key_to_set=k, value_to_set=v)