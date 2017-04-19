import os

import paramiko

hosts = [
        'pascal.cs.rutgers.edu'
        ]

class SSH(object):
    def __init__(self, host=hosts[0]):
        self._host = host
        self._client = paramiko.SSHClient()
        self._username = 'sv453'
        self._password = os.environ['SSH_PASSWORD']

        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.connect(
                self._host, 
                username=self._username, 
                password=self._password)

    def execute(self, command):
        ssh_stdin, ssh_stdout, ssh_stderr = self._client.exec_command('ls')
        return ssh_stdout.read()

    def close(self):
        self._client.close()

def main():

    ssh = SSH()
    print ssh.execute('ls')
    ssh.close()

if __name__ == '__main__':
    main()

