


class manager_rmi():

    def __init__(self, hostname, login, passwd, cmd):
        print 'manager_rmi instance'

        hostname
        login
        passwd
        cmd



        def rmi(self, hostname, login, passwd, cmd, callback=None):
            while True:
                try:
                    s = pxssh.pxssh()
                    s.login(hostname, login, passwd)
                    s.timeout = 3600  # set timeout to one hour
                    s.sendline('whoami')
                    s.prompt()  # match the prompt
                    s.sendline(cmd)  # run a command
                    s.prompt() # true
                    last_output = s.before  # # # print everyting before the prompt
                    print colored(last_output, 'blue')
                    s.logout()
                except pxssh.ExceptionPxssh, e:
                    continue
                break
            print "LAST: OUTPUT"
            print last_output
            replace_n = last_output.replace('\n', '')
            replace_r = replace_n.replace('\r', '')
            whole_cmd = replace_r.split(' ')
            print "JOIN COMMAND: "
            join_cmd = ''.join(whole_cmd[-2:])
            print "AFTER JOIN "
            print join_cmd
            return join_cmd

        def rmisandBox(self, hostname, login, passwd, cmd, callback=None):
            sandboxIP = SANDBOX_STATIC_IP
            sandboxUser = VAGRANT_DEFAULT_LOGIN
            sandboxPass = VAGRANT_DEFAULT_LOGIN
            str_cmd = " " \
                      'sshpass -p {} ssh -f -n -o StrictHostKeyChecking=no {}@{} "{}"' \
                      " ".format(sandboxPass, sandboxUser, sandboxIP, cmd)

            # return "asdasdf"
            return self.rmi(hostname, login, passwd, str_cmd)

        def rmibenchBox(self, hostname, login, passwd, cmd, callback=None):
            benchboxIP = BENCHBOX_STATIC_IP
            benchboxUser = VAGRANT_DEFAULT_LOGIN
            benchboxPass = VAGRANT_DEFAULT_LOGIN
            str_cmd = " " \
                      'sshpass -p {} ssh -f -n -o StrictHostKeyChecking=no {}@{} "{}"' \
                      " ".format(benchboxPass, benchboxUser, benchboxIP, cmd)

            # return 'asdf'
            return self.rmi(hostname, login, passwd, str_cmd)

        # this is auxiliary rmi function has ssh -f -n unset
        def rmiStatus(self, hostname, login, passwd, cmd, localhost):
            # # print localhost
            if localhost == 'localhost':
                # # print "LOCALHOST_::"
                result = self.rmi(hostname, login, passwd, cmd)
                print "RMI LOCALHOST RESULT {}: {}".format(localhost, result)
                """
                str = result
                print result
                result = str.split('\n', 1)  # split once
                """
                return result
            elif localhost == 'sandBox':
                boxIP = SANDBOX_STATIC_IP
            elif localhost == 'benchBox':
                boxIP = BENCHBOX_STATIC_IP


            boxUser = VAGRANT_DEFAULT_LOGIN
            boxPass = VAGRANT_DEFAULT_LOGIN

            str_cmd = " " \
                      'sshpass -p {} ssh -o StrictHostKeyChecking=no {}@{} "{}"' \
                      " ".format(boxPass, boxUser, boxIP, cmd)
            # return 'asdf'
            result = self.rmi(hostname, login, passwd, str_cmd)

            print "RMI RESULT {}: {}".format(localhost, result)

            return result
