
# source -> target folder

TGTFOLDER=$1

#Stop dropbox
~/dropbox.py stop
#Backup your Dropbox database.
cp ~/.dropbox/dropbox.db dropbox.db.backup
#Get the Python script for helping changing the directory location
wget http://dl.dropbox.com/u/119154/permalink/dropboxdir.py
#Change permission to to execute the new python script.
chmod +x dropboxdir.py
#Move your current Dropbox directory to a new location
#”/path/to/newDropbox/location”
mv ~/Dropbox /path/to/newDropbox/location
#Tell Dropbox to use the new directory location
./dropboxdir –setfolder=/path/to/newDropbox/location
#Start Dropbox.
~/dropbox start