# Kisscartoon Batch Downloader

Get's and downloads Videos from Kisscartoon

# Usage


```./python kisscartoon.py <cartoon page> ```

If you don't want extra Information just the download add -q or --quiet
```./python kisscartoon.py -q <cartoon page> ```

If you want to handle the downloading yourself use --only-links or -l to just print the links
```./python kisscartoon.py -l <cartoon page> ```

If you want the links written to a File use --save-links or -s to save them to links.txt
```./python kisscartoon.py -s <cartoon page> ```

Those Operators are freely combinable


```./python kisscartoon.py -q -s http://kisscartoon.me/Cartoon/Aqua-Teen-Hunger-Force-Season-10```

# Requirements

Python :
* cfscrape
* BeautifulSoup4 ( bs4 )
* pySmartDL

All of the dependencies are available via pip and easy_install


 


