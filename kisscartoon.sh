#!/bin/sh

#Deleting the old list
rm -f list.txt

#Color Codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
BOLD=$(tput bold)
NORMAL=$(tput sgr0)
XCLIP=0

#Checking if Spidermonkey is present
if [ -n "$(which js)" ]; then
    echo "$YELLOW$BOLD"$(date +[%H:%M:%S])"$NC${GREEN}${BOLD} Spidermonkey${NORMAL} seems to be installed${NC}"
else
    echo "$YELLOW$BOLD"$(date +[%H:%M:%S])"$NC${RED}${BOLD} Spidermonkey${NORMAL} not found please install it${NC}"
    exit 0
fi

#Checking if xclip is present
if [ -n "$(which xclip)" ]; then
    echo "$YELLOW$BOLD"$(date +[%H:%M:%S])"$NC${GREEN}${BOLD} xclip${NORMAL} seems to be installed${NC}"
else
    echo "$YELLOW$BOLD"$(date +[%H:%M:%S])"$NC${RED}${BOLD} xclip${NORMAL} not found. Can't copy links to clipboard.${NC}"
fi


#Starting the Link Grabber
wget -qO- $1 | grep '<a href="/Cartoon/' | grep "?id=" | grep -o '/[^"]*' | sed -e 's/^/kisscartoon.me/' |  xargs -L 1 ./getlink.sh

echo "$YELLOW$BOLD"$(date +[%H:%M:%S])"$NC The Download Links are in ${GREEN}${BOLD}links.txt${NORMAL}${NC}"

if [ $# -ne 0 ]; then

    if [ $2 = "-c" ]; then
        if [ $XCLIP -ne 0 ]; then 
            echo "$YELLOW$BOLD"$(date +[%H:%M:%S])"$NC Copied Links to clipboard${NC}"
        else
            echo "$YELLOW$BOLD"$(date +[%H:%M:%S])"$NC$RED$BOLD xclip$NORMAL not installed${NC}"
        fi
    fi

fi
