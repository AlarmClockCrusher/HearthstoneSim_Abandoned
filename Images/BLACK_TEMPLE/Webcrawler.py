import requests
import bs4 as bs
import urllib.request

url = str(input("URL		))

opener = urllib.request.build_opener()
opener.add_headers = [{"User-Agent"		Mozilla"}]
urllib.request.install_opener(opener)

raw = requests.get(url).text
soup = bs.BeautifulSoup(raw, "html.parser")

imgs = soup.find_all('img')
links = []

for img in imgs:
	link = img.get('src')
	if 'http://' not in link:
		link = url + link
	links.append(link)
	
print("Images detected: %d"%len(links))
for i in range(len(links)):
	filename = "img{}.png".format(i)
	urllib.request.urlretrieve(links[i], filename)
	print("Done!")