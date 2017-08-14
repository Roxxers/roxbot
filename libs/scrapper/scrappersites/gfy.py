class gfycat():
	def __init__(self):
		pass

	def url_get(self,url,urladd):
		urlsplit = url.split("/")
		urlsplit[2] = urladd + urlsplit[2]
		urlsplit.append(".webm")
		i = 0
		urlnew = ""
		for split in urlsplit:
			urlnew = urlnew + split
			i += 1
			if i <= 3:
				urlnew = urlnew + "/"
		return urlnew

	def get(self,url):
		return url