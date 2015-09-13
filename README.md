# Kisscartoon Batch Downloader

Get's and downloads Videos from Kisscartoon

# Changelog

* Download can now be canceled with Ctrl + C
* Added low quality video feature
* Fixed a bug that made the Script crash on OS'es that aren't Windows.

# Usage


```./python kisscartoon.py <cartoon page> ```

If you don't want extra Information just the download add -q or --quiet

```./python kisscartoon.py -q <cartoon page> ```

If you want to handle the downloading yourself use --only-links or -l to just print the links

```./python kisscartoon.py -l <cartoon page> ```

If you want the links written to a File use --save-links or -s to save them to links.txt

```./python kisscartoon.py -s <cartoon page> ```

If you don't want the highest quality ( it's the default setting ) you can add -a or --low-quality to get the lowest available quality

```./python kisscartoon.py -a <cartoon page> ```


Those Operators are freely combinable


```./python kisscartoon.py -q -s http://kisscartoon.me/Cartoon/Aqua-Teen-Hunger-Force-Season-10```

# Requirements

Python :

* [cfscrape](https://github.com/Anorov/cloudflare-scrape/)
  * requests
  * PyExecJS
  * A JavaScript Engine (Like Node or PyV8)
* [BeautifulSoup4 ( bs4 )](https://pypi.python.org/pypi/beautifulsoup4)
* [pySmartDL](https://pypi.python.org/pypi/pySmartDL/)

All of the dependencies are available via pip and easy_install


 


