import sys, json;

existing_env_vars = json.loads(sys.argv[1])
cognito_vars = json.loads(sys.argv[2])

# print("existing_env_vars: ", existing_env_vars)
# print("existing_env_vars type: ", type(existing_env_vars))
# print("cognito_vars: ", cognito_vars)
# print("cognito_vars type: ", type(cognito_vars))

def assign_cognito_vars():
    for key, value in cognito_vars.items():
        # print(key, value)
        existing_env_vars[key] = value


if existing_env_vars == None:
    existing_env_vars = {}
    assign_cognito_vars()
    
else:
    assign_cognito_vars()

print(json.dumps(existing_env_vars))

