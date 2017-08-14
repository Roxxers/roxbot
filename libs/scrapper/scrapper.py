import os
from libs.scrapper.scrappersites import imgur, reddit, gfy, tumblr

class scrapper():
	def __init__(self):
		pass

	def get(self, url):
		url2 = ""
		if "imgur" in url:
			url2 = imgur.imgur().get(url)
		elif "gfycat" in url:
			url2 = gfy.gfycat().get(str(url))
		elif "eroshare" in url:
			#eroshare.eroshare().get(url)
			pass
		elif "redd.it" in url or "i.reddituploads" in url:
			url2 = reddit.reddit().get(url)
		elif "media.tumblr" in url:
			url2 = tumblr.tumblr().get(url)
		return url2

