# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2017-2018 Roxanne Gibson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import json
import aiohttp


async def request(url, *, headers=None, **kwargs):
	"""Base GET request in case you need more control over GET requests.

	Params
	=======
	headers: dict (Optional)
	kwarg: kwargs (Optional)

	Returns
	=======
	Response: aiohttp Response object
	"""
	async with aiohttp.ClientSession() as session:
		return await session.get(url, headers=headers, **kwargs)


async def api_request(url, *, headers=None, **kwargs):
	"""Returns JSON from an API request. Should be used for all Roxbot API requests.

	Params
	=======
	url: str
	headers: dict (Optional)
	kwargs: kwargs (Optional)

	Returns
	=======
	JSON response: dict
	"""
	if headers is None:
		headers = {'User-agent': 'RoxBot Discord Bot'}
	else:
		headers = {'User-agent': 'RoxBot Discord Bot', **headers}
	async with aiohttp.ClientSession() as session:
		async with session.get(url, headers=headers, **kwargs) as resp:
			try:
				output = await resp.text()
				return json.loads(output)
			except json.JSONDecodeError:
				return None


async def download_file(url, filename=None):
	"""Downloads the file at the given url and then saves it under the filename given to disk.

	Params
	=======
	url: str
	filename: str (Optional)
		if not given, the function will try and determine filename from url.

	Returns
	=======
	filename: str
		Handy if no filename given
	"""
	if filename is None:
		filename = url.split("/")[-1].split("?")[0]
	async with aiohttp.ClientSession() as session:
		async with session.get(url, headers={'User-agent': 'RoxBot Discord Bot'}) as data:
			with open(filename, 'wb') as f:
				f.write(await data.read())
	return filename


async def upload_file(url, file):
	"""Uploads a file using a POST request. Broke for pomf clones so idk. Might have to revert it to requests.

	:param url: url to POST to.
	:param file: Byes-like object to upload.
	:return:
	"""
	async with aiohttp.ClientSession() as session:
			payload = {"files": open(file, "rb")}
			resp = await session.post(url, headers={'User-agent': 'RoxBot Discord Bot', "content_type": "multipart/form-data"}, data=payload)
			return await resp.json()


async def get_page(url, *, headers=None, **kwargs):
	"""Returns the html of the given url. Will need to run it through BS4 to parse it.

	Params
	=======
	url: str

	Returns
	=======
	HTML Page: str
	"""
	async with aiohttp.ClientSession() as session:
		async with session.get(url, headers=headers, **kwargs) as page:
			return await page.text()
