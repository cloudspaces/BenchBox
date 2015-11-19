


def warmUp(self, h):
    str_cmd = "if [ -d ~/workload_generator ]; then; " \
              "cd ~/workload_generator; " \
              "python executor.py -o {} -p {} -t {} -f {} -x {} -w 1; " \
              "fi; ".format(0, 'backupsample', 0, 'stacksync_folder', 'StackSync')
    print str_cmd

def tearDown(self, h):
    str_cmd = "if [ -d ~/output ]; then " \
              "rm -R ~/output; " \
              "fi; "

def vagrantDown(self, h):
    str_cmd = "kill -9 $(pgrep ruby); " \
              "kill -9 $(pgrep vagrant); " \
              "if [ -d BenchBox ]; then " \
              "cd BenchBox; " \
              "cd vagrant; " \
              "vagrant halt; " \
              "fi; "
    # print str_cmd
    self.rmi(h['ip'], h['user'], h['passwd'], str_cmd)

def vagrantUp(self, h):
    str_cmd = "" \
              "if [ -d BenchBox ]; then " \
              "cd BenchBox;" \
              "git pull; " \
              "cd vagrant; " \
              "echo '-------------------------------'; " \
              "ls -l *.box; " \
              "vagrant -v; " \
              "VBoxManage --version; " \
              "echo '-------------------------------'; " \
              "VBoxManage list runningvms | wc -l > running; " \
              "vagrant up sandBox; " \
              "vagrant provision sandBox; " \
              "vagrant up benchBox; " \
              "vagrant provision benchBox; " \
              "else " \
              "echo 'Vagrant Project not Found!??'; " \
              "fi;" \
              ""
    self.rmi(h['ip'], h['user'], h['passwd'], str_cmd)

def monitorUp(self, h):

    str_cmd = './monitor/startMonitor.sh'
    self.rmisandBox(h['ip'], h['user'], h['passwd'], str_cmd)

def clientStackSyncUp(self, h):

    hostname = h['hostname'][0]
    str_cmd = 'nohup /usr/bin/stacksync &'
    self.rmisandBox(h['ip'], h['user'], h['passwd'], str_cmd)

def clientStackSyncDown(self, h):

    str_cmd = '/usr/bin/stacksync clear &'
    self.rmisandBox(h['ip'], h['user'], h['passwd'], str_cmd)

def clientOwnCloudUp(self, h):

    str_cmd = 'nohup /vagrant/owncloud.sh &'
    self.rmisandBox(h['ip'], h['user'], h['passwd'], str_cmd)
    # have session at the dummy host
