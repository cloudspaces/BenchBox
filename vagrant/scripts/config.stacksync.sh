#!/usr/bin/env bash



if [ ! -f "ss.stacksync.ip" ];
then
echo "File: not found!"
sync_server_ip=$1 # stacksync server_ip,
exit;
else
echo "File: $2 exists!"
fi

sync_server_ip=`more "ss.stacksync.ip" | awk -F ' ' '{ print $2}' | awk -F ':' '{print $1}'`
if [ -z $sync_server_ip ];
then
	echo 'user next path'
	sync_server_ip=($(<"ss.stacksync.ip"))
else
	echo 'already read once'
	echo $sync_server_ip
fi



sync_server_port=`more "ss.stacksync.port" | awk -F ' ' '{ print $2}' | awk -F ':' '{print $1}'`
if [ -z $sync_server_port ];
then
	echo 'user next path'
	sync_server_port=($(<"ss.stacksync.port"))
else
	echo 'already read once'
	echo $sync_server_port
fi

if [ ! -f "ss.stacksync.key" ];
then
echo "File: not found!"
exit;
else
echo "File: $1 exists!"
fi

line=($(<"ss.stacksync.key"))


stacksync_key=$line


IFS=',' read -a myarray <<< "$stacksync_key"

ID=${myarray[0]}
USER=${myarray[1]}

SWIFT_AUTH=${myarray[2]}
SWIFT_USER=${myarray[3]}

EMAIL=${myarray[4]}


swift_group='stacksync'
swift_user=$SWIFT_USER
username='vagrant'
id=$ID
email=$EMAIL
password=$USER
FILE='config.xml'

cat > $FILE <<- EOM

<stacksync>
    <!--
    <username>$username</username>
    <queuename>$hostname</queuename>
    <autostart>true</autostart>
    <notifications>true</notifications>
    -->
    <!--
    <apiLogUrl>http://localhost/stack/apiput</apiLogUrl>
    <apiLogUrl>URL_LOG_SERVER_API</apiLogUrl>
    -->
    <remoteLogs>false</remoteLogs>

    <rabbitMQ>
        <host>$sync_server_ip</host>

        <port>sync_server_port</port>
        <enableSSL>false</enableSSL>

        <username>guest</username>
        <password>guest</password>
        <rpc_exchange>rpc_global_exchange</rpc_exchange>
    </rabbitMQ>

    <cache>
        <size>1024</size>
        <folder>/home/$username/.stacksync/cache</folder>
    </cache>

<device>
        <name>sandBox</name>
    </device>
    <profile>
        <enabled>true</enabled>
        <name>(unknown)</name>
        <repository>
            <chunksize>512</chunksize>
            <connection type="swift_comercial">
                <username>$swift_group:$swift_user</username>
                <apikey>$password</apikey>
                <authurl>http://$sync_server_ip:5000/v2.0/tokens</authurl>
            </connection>
        </repository>
        <folder>
            <active>true</active>
            <local>/home/$username/stacksync_folder</local>
        </folder>
        <account>
            <id>$id</id>
            <email>$email</email>
            <password>$password</password>
        </account>
    </profile>
</stacksync>

EOM


if [[ -s $FILE ]] ; then
echo "$FILE has data."
else
echo "$FILE is empty."
fi ;
ls -l $FILE
echo 'New credentials generated successfully!!'



