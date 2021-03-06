import pythoncom
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
from prod_status import ProdStatusService

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "TestService"
    _svc_display_name_ = "Test Service"

    def __init__(self,args):
        self.ps = ProdStatusService()

        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):

        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        self.ps.stop()
        win32event.SetEvent(self.hWaitStop)


    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        # kill all existing python process but not self



        self.main()

    def main(self):
        # here goes the call to main script
        print "Running Prod_Status"
        # loop().start()
        self.ps.main(status_msg='provisionOK', topic=socket.gethostname())


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)