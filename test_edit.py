import requests

# Hardcoded values
API_KEY = "IoNXt5EHaksrrvP4T9s3733o1xeNkNRxxMECYcPe4SCMJt6daePLacKFmyxYMlLy9evKiM795BqE7suoST3VIw"
IMAGE_PATH = "/home/federico/Desktop/personal/book_publishing_api/output/images/ember_the_little_dragons_first_adventure/page_02.png"
MASK_PATH = "path/to/your/mask_image.jpg"  # Black/white mask where black = areas to edit

url = "https://api.ideogram.ai/v1/ideogram-v3/edit"

headers = {
    "Api-Key": API_KEY
}

# Open files and prepare form data
with open(IMAGE_PATH, 'rb') as img_file, open(MASK_PATH, 'rb') as mask_file:
    files = {
        'image': img_file,
        'mask': mask_file
    }
    
    data = {
        'prompt': "A character floating in outer space with stars, planets and cosmic background",
        'rendering_speed': "DEFAULT",
        'num_images': 1
    }
    
    response = requests.post(url, headers=headers, files=files, data=data)

if response.status_code == 200:
    result = response.json()
    image_url = result['data'][0]['url']
    print(f"Success! Edited image URL: {image_url}")
else:
    print(f"Error: {response.status_code} - {response.text}")