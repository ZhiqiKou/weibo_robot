import requests

print("开始下载")

result = requests.Session()
url = 'http://baobab.kaiyanapp.com/api/v1/playUrl?vid=155956&resourceType=video&editionType=default&source=aliyun&playUrlType=url_oss'
#url = 'http://ali.cdn.kaiyanapp.com/032f2d4a7ec141c31bac711cf0475c52_1280x720.mp4?auth_key=1554390034-0-0-cdbefbb9e47b13ef26a99baa41a43f90'

headers = {
    'Host': 'baobab.kaiyanapp.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36'
}
r = result.get(url, headers=headers, allow_redirects=False)
location = r.headers['Location']
print(location)
nr = requests.get(location, stream=True)
with open('test.mp4', "wb") as mp4:
    for chunk in nr.iter_content(chunk_size=1024 * 1024):
        if chunk:
            mp4.write(chunk)

print("下载结束")