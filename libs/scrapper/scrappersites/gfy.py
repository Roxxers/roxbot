class gfycat():
	def __init__(self):
		pass

	def url_get(self,url):
		urlsplit = url.split("/")
		urlsplit[2] = "giant." + urlsplit[2]
		urlsplit[-1] += ".gif"
		urlnew = "/".join(urlsplit)
		return urlnew

	def get(self,url):
		#url2 = self.url_get(url)
		url2 = url
		return url2