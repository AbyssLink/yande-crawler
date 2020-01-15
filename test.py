import requests
from tqdm import tqdm

headers: dict = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/75.0.3770.142 '
                  'Safari/537.36'
}

url = "https://files.yande.re/image/75bbf80698c4b354a74744a981932290/yande.re%20602573%20triangle%21%20wallpaper%20yatomi.jpg"  # big file test
# Streaming, so we can iterate over the response.
r = requests.get(url=url, headers=headers, stream=True)
status = r.status_code

if status == 200:
    # Total size in bytes.
    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    t = tqdm(total=total_size, unit='iB', unit_scale=True)
    with open('test.jpg', 'wb') as f:
        for data in r.iter_content(block_size):
            t.update(len(data))
            f.write(data)
    t.close()
    if total_size != 0 and t.n != total_size:
        print("ERROR, something went wrong")
