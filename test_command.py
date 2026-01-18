import requests

tests = [
    ("What is ahead?", "WHAT_IS_AHEAD", None),
    ("Take me to the cafeteria", "NAVIGATE_TO_DESTINATION", "cafeteria"),
    ("Describe my surroundings", "DESCRIBE_SURROUNDINGS", None),
    ("Is it safe?", "SAFETY_CHECK", None),
    ("Go to washroom", "NAVIGATE_TO_DESTINATION", "washroom"),
    ("Take me to the library", "UNKNOWN", None),
]

print("Testing command interpretation:\n")
for text, expected_intent, expected_dest in tests:
    r = requests.post('http://127.0.0.1:8000/command/interpret', json={'text': text})
    result = r.json()
    match = result['intent'] == expected_intent and result.get('destination') == expected_dest
    status = '✓' if match else '✗'
    print(f'{status} "{text}"')
    print(f'  Got: {result["intent"]}, {result.get("destination")}')
    print(f'  Expected: {expected_intent}, {expected_dest}\n')
