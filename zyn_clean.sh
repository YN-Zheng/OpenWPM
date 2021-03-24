set -x
pkill python
pkill wpr
mkdir 
DEST=$(date +"%d_%I:%M")
mkdir tmp/$DEST
mv datadir tmp/$DEST
mv crawl.log tmp/$DEST
mv replay.log tmp/$DEST
mv nohup.out tmp/$DEST