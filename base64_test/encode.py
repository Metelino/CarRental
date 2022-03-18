import base64
from pathlib import Path
import imghdr

BASE_DIR = Path(__file__).resolve().parent
print(f'Ścieżka: {BASE_DIR}')

f = open(f"{BASE_DIR}/sony.jpg", "rb")
#print(f.read())
img_bytes = f.read()
ext = imghdr.what(None, h=img_bytes)
print(ext)
base64_img_bytes = base64.b64encode(img_bytes)
print(f'BASE64:\n{base64_img_bytes}')