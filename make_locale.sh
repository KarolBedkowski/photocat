#!/bin/bash

mkdir locale 2>/dev/null

for i in po/*.po; do
	echo "$i...."
	loc="${i:3:2}"
	mkdir -p locale/$loc/LC_MESSAGES
	msgfmt $i -o locale/$loc/LC_MESSAGES/pc.mo
done;

