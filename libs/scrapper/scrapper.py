import requests
import random
from libs.scrapper.scrappersites import imgur, reddit, gfy, tumblr

class scrapper():
	def __init__(self):
		pass

	def linkget(self, subreddit, israndom):
		if israndom:
			options = [".json?count=100", "/top/.json?sort=top&t=all&count=100"]
			choice = random.choice(options)
			subreddit += choice
		html = requests.get("https://reddit.com/r/"+subreddit, headers = {'User-agent': 'RoxBot Discord Bot'})
		try:
			reddit = html.json()["data"]["children"]
		except KeyError:
			return False
		return reddit

	def retriveurl(self, url):
		url2 = ""
		if "imgur" in url:
			url2 = imgur.imgur().get(url)
		elif "gfycat" in url:
			url2 = gfy.gfycat().get(url)
		elif "eroshare" in url:
			#eroshare.eroshare().get(url)
			pass
		elif "redd.it" in url or "i.reddituploads" in url:
			url2 = reddit.reddit().get(url)
		elif "media.tumblr" in url:
			url2 = tumblr.tumblr().get(url)
		print(url)
		return url2