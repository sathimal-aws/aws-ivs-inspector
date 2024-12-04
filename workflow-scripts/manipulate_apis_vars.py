import sys, json;

existing_env_vars = json.loads(sys.argv[1])
region = sys.argv[2]
api_values = json.loads(sys.argv[3])
account_id = sys.argv[4]
 
existing_env_vars[region] = api_values
existing_env_vars["VITE_ACCOUNT_ID"] = account_id

region_keys = list(map(lambda x: x.replace("VITE_API_", ""), [k for k in existing_env_vars.keys() if "VITE_API_" in k]))
existing_env_vars["VITE_IVS_REGIONS"] = ",".join(region_keys)

print(json.dumps(existing_env_vars))

