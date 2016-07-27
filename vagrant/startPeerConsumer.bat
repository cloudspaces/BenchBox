


echo "Starting sandBox prod status"

:: python C:\Users\vagrant\vagrant\prod_status.py --msg provisionWindows --topic none
python C:\Users\vagrant\vagrant\winService.py stop
python C:\Users\vagrant\vagrant\winService.py remove
python C:\Users\vagrant\vagrant\winService.py install
python C:\Users\vagrant\vagrant\winService.py start

:: --msg provisionOK --topic %ComputerName%  --windows True
:: this is a batch comment

echo "How to know if the startPeerConsumer is running??"













