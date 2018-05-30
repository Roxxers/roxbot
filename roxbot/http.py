# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2017-2018 Roxanne Gibson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import json
import aiohttp


async def request(url, *, headers=None, **kwargs):
	"""
	Base GET request.
	:param url:
	:param headers:
	:param kwargs:
	:return:
	"""
	async with aiohttp.ClientSession() as session:
		return await session.get(url, headers=headers, **kwargs)


async def api_request(url, *, headers=None, **kwargs):
	"""
	Returns a JSON dict object for most api calls in RoxBot.
	:param url: URL Should be a api endpoint that will return
	:param headers: There is no need to pass the user agent, this is done for you.
	:return: dict of JSON or None if a JSON was not returned from the call.
	"""
	if headers is None:
		headers = {'User-agent': 'RoxBot Discord Bot'}
	else:
		headers = {'User-agent': 'RoxBot Discord Bot', **headers}
	resp = await request(url, headers=headers, **kwargs)
	try:
		return json.loads(await resp.read())
	except json.JSONDecodeError:
		return None


async def download_file(url, filename=None):
	"""
	Downloads the file at the given url and then saves it under the filename given to disk.
	:param filename:
	:param url:
	"""
	if filename is None:
		filename = url.split("/")[-1].split("?")[0]
	async with aiohttp.ClientSession() as session:
		async with session.get(url, headers={'User-agent': 'RoxBot Discord Bot'}) as data:
			with open(filename, 'wb') as f:
				f.write(await data.read())
	return filename


async def upload_file(url, file):
	"""

	:param url: url to POST to.
	:param file: Byes-like object to upload.
	:return:
	"""
	async with aiohttp.ClientSession() as session:
			payload = {"files": open(file, "rb")}
			resp = await session.post(url, headers={'User-agent': 'RoxBot Discord Bot', "content_type": "multipart/form-data"}, data=payload)
			return await resp.json()


async def get_page(url):
	"""
	Returns the page at the given url
	:param url: the url of the page you want to get
	:return: the html page
	"""
	async with aiohttp.ClientSession() as session:
		async with session.get(url, headers={'User-agent': 'RoxBot Discord Bot'}) as page:
			return await page.text()
