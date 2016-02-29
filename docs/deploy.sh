#! /bin/sh

cd _build/html
rsync -avz -e "ssh" --progress . thrawn01.org.bast:/usr/share/nginx/html/subcommand
