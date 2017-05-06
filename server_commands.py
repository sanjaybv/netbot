import os
from os import system as system_call

import paramiko

hosts = [
        'pascal.cs.rutgers.edu',
        'top.cs.rutgers.edu',
        'prolog.cs.rutgers.edu',
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
        return ssh_stdout.read(), ssh_stderr.read()

    def close(self):
        self._client.close()

# returns error
def deploy(repo_url, server_name):
    '''
    Steps to deploy:
    1. Validate url (done in wit_actions)
    2. Validate server_name
    3. Ping to server
    3. SSH to server
    4. go get repo (go get should build automatically for main pkgs)
    5. Run repo name
    '''

    # validate server_name
    if not any([server_name in x for x in hosts]):
        return "Server name does not exist"

    # get correct server url
    for host in hosts:
        if server_name in host:
            server_url = host
            break

    # ping to check if host is alive
    if not ping(server_url):
        return "Server does not exist"

    # ssh to server
    ssh_client = SSH(server_url)

    # run go get command
    out, err = ssh_client.execute("go get " + repo_url)
    if err != '':
        return err

    return None

def get_hosts_status():
    statuses = []
    for host in hosts:
        statuses.append((host, "online" if ping(host) else "offline"))
    return statuses

def ping(host):
    return system_call("ping -c 1 " + host) == 0

def main():

    ssh = SSH()
    print ssh.execute('ls')
    ssh.close()

if __name__ == '__main__':
    main()
