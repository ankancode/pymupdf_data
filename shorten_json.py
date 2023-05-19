import json


def shorten_json(data):
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                result[key] = shorten_json(value)
            elif value not in result.values():
                result[key] = value
        return result
    elif isinstance(data, list):
        return [shorten_json(item) for item in data]
    else:
        return data

if __name__ == "__main__":

    # Example JSON data
    json_data = {
        "key1": "value1",
        "key2": {
            "key3": "value3",
            "key4": ["item1", "item2", {"key5": "value5"}]
        },
        "key6": "value1",
        "key7": {
            "key8": {
                "key9": "value9"
            }
        },
        "key10": ["item1", "item2", "item1", "item3"]
    }
    json_path = input("json_path: ")
    with open(json_path) as f:
        json_data = json.loads(f.read()) 
    # Shorten the JSON structure
    shortened_json = shorten_json(json_data)

    # Print the shortened JSON
    with open("shortened_json.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(shortened_json, indent=4))
