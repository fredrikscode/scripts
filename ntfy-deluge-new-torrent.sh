#!/bin/bash

torrentid=$1
torrentname=$2
torrentpath=$3
$token="tk_xxxxxxxxxxx"
$ntfy_endpoint="https://ntfy.mydomain.com/topic"

echo "Torrent Details: " "$torrentname" "$torrentpath" "$torrentid"  >> /tmp/execute_script.log

curl -H "Authorization: Bearer $token" -H "Title: Torrent added" -H "Tags: file_folder" -d "$2" $ntfy_endpoint
