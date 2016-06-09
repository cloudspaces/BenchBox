


echo "Starting sandBox prod status"



start /B pythonw C:\Users\vagrant\vagrant\prod_status.py --msg provisionOK --topic %ComputerName% --windows True
:: this is a batch comment

echo "How to know if the startPeerConsumer is running??"













