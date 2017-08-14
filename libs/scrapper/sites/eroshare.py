
class eroshare():
	def __init__(self):
		pass

	def get(self,url, name):
		page = requests.get(url)
		tree = html.fromstring(page.content)
		links = tree.xpath('//source[@src]/@src')
		if links:
			album_create(name)
			for link in links:
				if "lowres" not in link:
					wget.download(link)
					print("Downloaded ", link)
		links = tree.xpath('//*[@src]/@src')
		if len(links) > 2 and not album_create.hasbeencalled:
			album_create(name)
		for link in links:
			if "i." in link and "thumb" not in link:
				if link.split("/")[-1] not in os.listdir("./"):
					wget.download("https:" + link)
					print("Downloaded ", link)
				else:
					print("Already exists")
		if album_create.hasbeencalled:
			os.chdir("../")
			album_create.hasbeencalled = False