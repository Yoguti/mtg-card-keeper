import requests as r
import sys
import time
import ijson
from PIL import Image
from urllib.request import urlopen
import os

def write_to_file(FILE_PATH, url, custom_headers):
    if not os.path.exists(FILE_PATH):
        os.makedirs(FILE_PATH)
        print(f"Created directory: {FILE_PATH}")
    response = r.get(url, headers=custom_headers)
    data = response.json()

    unique_art = None
    for item in data['data']:
        if item['type'] == 'unique_artwork':
            unique_art = item
            break
    download_uri = unique_art['download_uri']

    with urlopen(download_uri) as source:
        objects = ijson.items(source, 'item')
        count = 0
        for card in objects:
            if 'image_uris' in card and 'normal' in card['image_uris']:
                card_id = card['id']
                card_jpg_url = card['image_uris']['normal']
        
                file_extension = "jpg" 
                file_name = f"{card_id}.{file_extension}"
                full_save_path = os.path.join(FILE_PATH, file_name)

                if os.path.exists(full_save_path):
                    continue
                try:
                    img_resp = r.get(card_jpg_url, stream=True, headers=custom_headers)
                    img_resp.raw.decode_content = True
                    
                    img = Image.open(img_resp.raw)
                    img.save(full_save_path)
                    
                    count += 1
                    if count % 10 == 0:
                        print(f"[{count}] Saved {file_name}")
                        
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"ERROR downloading {card_id}: {e}")
                    # Sleep a bit longer if we hit an error (backoff)
                    time.sleep(1)

if __name__ == "__main__":
    url = 'https://api.scryfall.com/bulk-data'
    custom_headers = {
        'User-Agent': 'azorius-on-top/0.1',
        'Accept': '*/*'
    }
    if len(sys.argv) != 2:
        print("Usage: python card-collect.py <file_path>")
        sys.exit(1)
    
    file_path_arg = sys.argv[1]
    write_to_file(file_path_arg, url, custom_headers)
