import os
from os import system as system_call

import paramiko
import urllib2
import requests

hosts = [
        'pascal.cs.rutgers.edu',
        'top.cs.rutgers.edu',
        'prolog.cs.rutgers.edu',
        'notexists.cs.rutgers.edu',
        'sanjaybv.github.com',
        ]

services = []

class SSH(object):
    def __init__(self, host=hosts[0]):
        self._host = host
        self._client = paramiko.SSHClient()
        self._username = 'sv453'
        self._password = os.environ['SSH_PASSWORD']
        self._pre_command = '. ~/.profile;'

        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.connect(
                self._host, 
                timeout=2.0,
                username=self._username, 
                password=self._password)

    def execute_exit_status(self, command):
        chan = self._client.get_transport().open_session()
        chan.exec_command(self._pre_command + command)
        
        return chan.recv_exit_status()#, chan.recv_stderr(1e100)

    def execute(self, command, need_output=True):
        ssh_stdin, ssh_stdout, ssh_stderr = self._client.exec_command(
                            self._pre_command + command)
        print '$ {0}'.format(command)
        if need_output:
            out, err = ssh_stdout.read(), ssh_stderr.read()
            print '{0} \n--\n {1}'.format(command, out, err)
            return out, err
        return None, None

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

    # validate github repo
    if not check_github_repo(repo_url):
        return "GitHub repo does not exist"

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
        return "That server does not exist." + \
            " Here is the status of the servers." + get_hosts_status()

    # ssh to server
    try:
        ssh_client = SSH(host=server_url)
    except Exception as e:
        return "There was a problem while contacting the server.\n" + str(e)

    # run go get command
    cmd = 'go get -u {0}'.format(repo_url)
    exit_status = ssh_client.execute_exit_status(cmd)
    if exit_status != 0:
        ssh_client.close()
        return 'go get error: exit_status = {0}'.format(exit_status)

    # create log folder
    log_path = '~/.netbot/' + repo_url
    cmd = 'mkdir -p ' + log_path
    out, err = ssh_client.execute(cmd)
    if err != '':
        ssh_client.close()
        return err

    # extract service name and run
    service_name = repo_url.split('/')[-1]
    cmd = '{0} > {1}/output.txt 2> {1}/error.txt &'.format(service_name, log_path)
    out, err = ssh_client.execute(cmd)
    if err != '':
        ssh_client.close()
        return err

    # get process id
    cmd = 'pgrep ' + service_name
    out, err = ssh_client.execute(cmd)
    if err != '':
        ssh_client.close()
        return err
    try:
        process_id = int(out.strip())
    except Exception as e:
        return 'Error getting process ID'

    # add to services
    services.append({
        'repo_url': repo_url,
        'server_name': server_name,
        'process_id': process_id,
        'log_path': log_path,
        })

    ssh_client.close()
    return None

def get_hosts_status():
    statuses = []
    for host in hosts:
        statuses.append((host, "online" if ping(host) else "offline"))

    status = '\n' + '\n'.join([(h + ' - ' + s) for h, s in statuses])
    return status

def ping(host):
    return system_call("ping -c 1 " + host) == 0

def check_github_repo(repo_url):

    url = list(repo_url.partition('github.com'))

    url[0] = 'https://' + url[0] + 'api.'
    url[2] = '/repos' + url[2]

    url = url[0] + url[1] + url[2]

    
    r = requests.get(url)
    if len(r.json()) == 2:
        return False
    else:
        return True

def get_service_status(repo_url, server_name):
    if ~ping(server_name):
        return "There's no server with that name"

    if not check_github_repo(repo_url):
        return "Github URL does not exist"


def main():

    ssh = SSH()
    print ssh.execute('ls')
    ssh.close()

if __name__ == '__main__':
    main()
