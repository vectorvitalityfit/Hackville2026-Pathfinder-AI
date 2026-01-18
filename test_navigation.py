import requests
import json
import time

base_url = 'http://127.0.0.1:8000/navigation'

def test_nav():
    # 1. Start Navigation
    print('1. Starting navigation to cafeteria...')
    r = requests.post(f'{base_url}/start', json={'destination': 'cafeteria'})
    print(r.json())

    # 2. Simulate Frame (Using image.png)
    # image.png likely has "wood floor" and maybe some boxes.
    # If vision detects them as "center", we expect STOP.
    # If "left/right", we expect FORWARD + warning.
    
    print('\n2. Simulating frame guide...')
    with open('image.png', 'rb') as f:
        resp = requests.post(f'{base_url}/guide', files={'file': f})
        if resp.status_code != 200:
            print(f"Error: {resp.text}")
            return
            
        data = resp.json()
        print('--- OUTPUT ---')
        print(f'Step: {data["current_step"]}')
        print(f'Obstacles Detected: {len(data["obstacles"])}')
        if data["obstacles"]:
            print(f'First Obstacle: {data["obstacles"][0]["name"]} at {data["obstacles"][0]["position"]}')
        print(f'Speech: "{data["speech_text"]}"')
        print('--------------')

    # 3. Validation
    # We want to see if Step is STOP (safety) or FORWARD (clear)
    # and if Speech mentions the context.

if __name__ == "__main__":
    test_nav()
