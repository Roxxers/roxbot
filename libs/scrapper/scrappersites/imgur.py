import requests
from bs4 import BeautifulSoup

class imgur():
	"""Class for all interactions with Imgur"""
	def __init__(self):
		pass

	def removed(self,url):
		page = requests.get(url)
		soup = BeautifulSoup(page.content, 'html.parser')
		if "removed.png" in soup.img["src"]:
			return True
		else:
			return False

	def get(self, url):
		if url.split(".")[-1] in ("png", "jpg", "jpeg", "gif", "gifv"):
			return url
		#elif url.split(".")[-1] == "gifv":
		#	urlsplit = url.split(".")
		#	urlsplit[-1] = "gif"
		#	url = ".".join(urlsplit)
		#	return url"""
		else:
			if self.removed(url):
				return False
			page = requests.get(url)
			soup = BeautifulSoup(page.content, 'html.parser')
			links = []
			for img in soup.find_all("img"):
				if "imgur" in img["src"]:
					if not img["src"] in links:
						links.append(img["src"])

			for video in soup.find_all("source"):
				if "imgur" in video["src"]:
					if not video["src"] in links:
						links.append(video["src"])
			if len(links) > 1:
				return url
			else:
				print(links)
				if not "http" in links[0]:
					links[0] = "https:" + links[0]
				return links[0]
