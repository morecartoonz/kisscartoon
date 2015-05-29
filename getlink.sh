#!/bin/sh

# Config
USERNAME=username
PASSWORD=password

#Color Codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
BOLD=$(tput bold)
NORMAL=$(tput sgr0)

#Logging in
wget --save-cookies cookies.txt -q -o /dev/null --keep-session-cookies -O /dev/null --post-data="username=$USERNAME&password=$PASSWORD" "http://kisscartoon.me/Login"

echo "$YELLOW$BOLD"$(date +[%H:%M:%S])"$NC Getting Link for$GREEN$BOLD http://"$1"${NC}"

#Extracting Download Link
WRAPTEXT="$(wget --load-cookies cookies.txt --keep-session-cookies -o /dev/null -qO- "$1")"
STREAMKEY="$(python wraptext.py "$WRAPTEXT")"

#Decrypting their silly Javascript mumbo jumbo
echo $STREAMKEY > streamkey
LINKS="$(js unwrap.js)"

#Getting the first Link from the decrypted text
LINK=`echo $LINKS | tr ' ' '\n' | grep -m 1 -o 'href=['"'"'"][^"'"'"']*['"'"'"]' | sed -e 's/^href=["'"'"']//' -e 's/["'"'"']$//'`

if [ "$LINK" = "/Login" ]; then
    echo "$RED$BOLD Login failed$NC"
    exit 0
fi

#Saving the link to the list
echo $LINK >> list.txt

#Deleting the encrypted links
rm streamkey

