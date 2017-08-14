import requests
from bs4 import BeautifulSoup

class imgur():
	"""Class for all interactions with Imgur"""
	def __init__(self):
		pass

	def removed(self,url):
		page = requests.get(url)
		soup = BeautifulSoup(page.content, 'html.parser')
		if "removed.png" in soup.a["src"]:
			return True
		else:
			return False

	def get(self, url):
		if self.removed(url):
			return False
		
		if url.split(".")[-1] in ("png", "jpg", "jpeg", "gif", "gifv"):
			return url
		elif url.split("/")[-2] == "a":
			page = requests.get(url)
			soup = BeautifulSoup(page.content, 'html.parser')
			links = []
			for img in soup.find_all("img"):
				if "imgur" in img["src"]:
					if not img["src"] in links:
						links.append(img["src"])
			if len(links) > 1:
				return False
			else:
				return links[0]
