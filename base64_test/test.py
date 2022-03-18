import base64
from pathlib import Path
import imghdr

BASE_DIR = Path(__file__).resolve().parent
print(f'Ścieżka: {BASE_DIR}')

f = open(f"{BASE_DIR}/cygan.jpg", "rb")
#print(f.read())
img_bytes = f.read()
ext = imghdr.what(None, h=img_bytes)
print(ext)
base64_img_bytes = base64.b64encode(img_bytes)
#print(base64_img_bytes)
decoded_img_bytes = base64.b64decode(base64_img_bytes)
#print(decoded_img_bytes)

with open(BASE_DIR / f'dupa.{ext}', 'wb') as file_to_save:
        file_to_save.write(decoded_img_bytes)