import os
from urllib.request import url2pathname

pathname = 'aru:_hanayui (hello).jpg'
file_url = "https://files.yande.re/image/e3ebf82021a8d419ab13ed5fa9d8d3df/yande.re%20598262%20ass%20bike_shorts" \
           "%20garter%20japanese_clothes%20ninja%20pantsu%20skirt_lift%20sword%20tori_%28puru0083%29%20weapon.jpg"
print(url2pathname(os.path.basename(file_url)))
