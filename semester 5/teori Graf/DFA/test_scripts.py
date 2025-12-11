import requests
import json

# Define the endpoint
url = 'http://127.0.0.1:8000/api/compare-speed/'

# Data to send (List of plates to check)
payload = {
    "plates": [
        "B 1234 XY",   # Valid format
        "Z 9999 ZZ",   # Invalid format
        "D 8888 AA",   # Valid format
        "A 123 BC"     # Valid format
    ]
}

try:
    print("Testing Speed Comparison API...")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("Success!")
        print(f"DFA Time: {data['dfa_duration_ms']} ms")
        print(f"DB Time:  {data['db_duration_ms']} ms")
        print(f"Winner:   {data['winner']}")
    else:
        print(f"Failed. Status Code: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Error: {e}")
    print("Is the server running?")