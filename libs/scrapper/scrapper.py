import os
from sites import gfy, imgur, tumblr, reddit

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


"""def main(choice):
	print("====== Menu ======")
	print("1: Download Subreddit")
	print("2: Download User")
	print("3: Download Your Front Page")
	print("9: Settings")
	while choice == 0:
		try:
			choice = int(input("Choice: "))
			if choice == 1:
				reddit().menu()
			elif choice == 2 or choice == 3:
				print("Feature in development")
				choice = 0
			elif choice == 9:
				schoice = 0
				print("")
				print("")
				print("====== Settings ======")
				print("1: Run redditsub in debug mode")
				print("2: Run eroshare in debug mode")
				print("3: Run imguralbum in debug mode")
				print("4: Run gfycatget in debug mode")
				print("5: Run Imgur().Get() in debug mode")
				print("9: Exit Program")
				schoice = int(input("Choice: "))
				if schoice == 1:
					reddit().menu()
				elif schoice == 2:
					url = input("Url: ")
					eroshare().get(url,"Test")
				elif schoice == 3:
					id = input("ID: ")
					imgur().get_album(id,"Test")
				elif schoice == 4:
					url = input("Url: ")
					gfycat().get(url)
				elif schoice == 5:
					url = input("URL: ")
					imgur().get(url[::-1],"Test")
				elif schoice == 6:
					reddit().saved()
				elif schoice == 9:
					return True
				else:
					print("Can't even fucking select the right shit")
			else:
				print("Your choice doesn't exist")
				choice = 0
		except ValueError:
			print("Use an interger number to choose from the menu")
			choice = 0
"""
if __name__ == "__main__":
	varsetup()
	#spreadsheetsetup()
	print("Setting up Directory")
	os.chdir('/home/roxie/Storage_1/Hello')
	print("")
	exitchoice = False
	while exitchoice is False:
		exitchoice = main(0)
