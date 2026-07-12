import json


with open("mapping.json") as f:
    data: dict[str, str] = json.load(f)

# new_data = {}

# for key, value in data.items():
#     parts = key.split(" ")
#     if parts[-1].isnumeric() and len(parts) > 1:
#         name = " ".join(parts[:-1])
#     else:
#         name = key

    
    

#     new_data[name] = value


# with open("mapping.json", "w") as f:
#     json.dump(new_data, f)

new_data = data.copy()
try:
    for k, v in data.items():
        if v:
            continue

        new = input(f"English for `{k}` : ")

        new_data[k] = new.strip()
finally:
    with open("mapping.json", "w") as f:
        json.dump(new_data, f)
