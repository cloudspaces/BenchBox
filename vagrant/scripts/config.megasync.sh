#!/usr/bin/env bash


echo `pwd`

megaPidFile='/tmp/MegaSync.pid'


FILE='megasync.sh'

cat > $FILE <<- EOM
#!/usr/bin/env bash


if [ ! -f $megaPidFile ]
then
        echo 'Run the client [MEGA]'
else
        echo 'Restart the client [MEGA]'
        pid=\$(head -n 1 $megaPidFile)
        echo 'status'
        ps -p \$pid
        status=\$?

        if [ \$status -ne 0 ]
        then
                echo 'no such proc [MEGA]'
        else
                echo 'proc exists [MEGA]'
                kill -9 \$pid
        fi
fi
        echo \$PPID > $megaPidFile

if [ \$# -eq 1 ]
then
        delay=\$1
else
        delay=1
fi

echo 'Create the mega folder'
megacmd mkdir mega:/$1

while true; do
        echo 'DoSync'
        megacmd sync /home/vagrant/mega_folder mega:/$1 -conf='/home/vagrant/.megacmd.json'
        echo 'SyncingComplete'
        sleep \$delay
done

EOM


if [[ -s $FILE ]] ; then
echo "$FILE CREATED!!!"
else
echo "$FILE FAIL!?."
fi ;



ls -l $FILE
echo 'New credentials generated successfully!!'
chmod u+x $FILE
ls $FILE
