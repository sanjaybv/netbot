import os
from os import system as system_call

import paramiko
import urllib2
import requests
import pickle

hosts = [
        'pascal.cs.rutgers.edu',
        'top.cs.rutgers.edu',
        'prolog.cs.rutgers.edu',
        'notexists.cs.rutgers.edu',
        'sanjaybv.github.com',
        ]

services = []

try:
    services_file = pickle.load(open('services.pkl', 'rb'))
    if services_file:
        services = services_file
except:
    pass

class SCException(Exception):
    def init(self, message, error=None):
        Exception.__init__(self, message)
        self.error = error

class InvalidRepoException(SCException):
    pass

class InvalidServerNameException(SCException):
    pass

class ServerUnavailableException(SCException):
    pass

class SSHUnavailableException(SCException):
    pass

class GoGetException(SCException):
    pass

class SSH(object):
    def __init__(self, host=hosts[0]):
        self._host = host
        self._client = paramiko.SSHClient()
        self._username = 'sv453'
        # self._password = os.environ['SSH_PASSWORD']
        self._password = 'S@nju123456'
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
        raise InvalidRepoException("GitHub repo does not exist")

    # validate server_name
    if not any([server_name in x for x in hosts]):
        raise InvalidServerName("Server name does not exist")

    # get correct server url
    for host in hosts:
        if server_name in host:
            server_url = host
            break

    # ping to check if host is alive
    if not ping(server_url):
        raise ServerUnavailableException(
            "That server seems to be unavailable. Try another server. " + \
            "Here are the statuses of the servers." + get_hosts_status())

    # ssh to server
    try:
        ssh_client = SSH(host=server_url)
    except Exception as e:
        raise SSHUnavailableException(
            "There was a problem contacting the server. Try another server. " + \
            "Here are the statuses of the servers." + get_hosts_status())

    # run go get command
    cmd = 'go get -u {0}'.format(repo_url)
    exit_status = ssh_client.execute_exit_status(cmd)
    if exit_status != 0:
        ssh_client.close()
        raise GoGetException(
            'go get error: exit_status = {0}'.format(exit_status))

    # create log folder
    log_path = '~/.netbot/' + repo_url
    cmd = 'mkdir -p ' + log_path
    out, err = ssh_client.execute(cmd)
    if err != '':
        ssh_client.close()
        raise SCException("Error making log directory")

    # extract service name and run
    service_name = repo_url.split('/')[-1]
    cmd = '{0} > {1}/output.txt 2> {1}/error.txt &'.format(service_name, log_path)
    try:
        out, err = ssh_client.execute(cmd)
    except Exception as e:
        raise SCException("Could not start service: " + str(e), e)
    if err != '':
        ssh_client.close()
        raise SCException("Could not start service: " + err)

    # get process id
    cmd = 'pgrep ' + service_name
    try:
        out, err = ssh_client.execute(cmd)
    except Exception as e:
        raise SCException("Could not get process id: " + str(e), e)
    if err != '':
        ssh_client.close()
        raise SCException("Could not get process id: " + err)
    try:
        process_id = int(out.strip())
    except Exception as e:
        raise SCException("Could not get process id: " + str(e), e)

    # add to services
    services.append({
        'repo_url': repo_url,
        'server_name': server_name,
        'process_id': process_id,
        'log_path': log_path,
        'server_url': server_url,
        })

    pickle.dump(services, open('services.pkl', 'wb'))

    ssh_client.close()
    return None

def stop(repo_url, server_name):
    '''
    Steps to stop
    1. Validate url
    2. Validate server_name and translate
    3. Check services and get pid(s)
    4. SSH and check for each pid if pid is running
        - if yes, then stop it
        - else, say it was not executing
    '''

    # validate github repo
    if not check_github_repo(repo_url):
        raise InvalidRepoException("GitHub repo does not exist")

    # validate server_name
    if not any([server_name in x for x in hosts]):
        raise InvalidServerName("Server name does not exist")

    # get correct server url
    for host in hosts:
        if server_name in host:
            server_url = host
            break

    # ping to check if host is alive
    if not ping(server_url):
        raise ServerUnavailableException(
            "That server seems to be unavailable. Try another server. " + \
            "Here are the statuses of the servers." + get_hosts_status())

    # loop through services
    stopped_pids = []
    already_stopped_pids = []
    ssh_client = SSH(host=server_url)
    for service in services:
        if service['repo_url'] == repo_url \
            and service['server_url'] == server_url:

            pid = service['process_id']
            exit_status = ssh_client.execute_exit_status(
                            'ps -p {0}'.format(pid))
            if exit_status:
                already_stopped_pids.append(str(pid))
            else:
                exit_status = ssh_client.execute_exit_status(
                                'kill -9 {0}'.format(pid))
                stopped_pids.append(str(pid))

    status = ''
    if already_stopped_pids:
        status += 'These pids were already stopped: ' + \
                    ', '.join(already_stopped_pids) + '\n'
    if stopped_pids:
        status += 'These pids were stopped: ' + \
                    ', '.join(stopped_pids) + '\n'

    if status == '':
        status += 'No such services were running.\n'
                
    ssh_client.close()
    return status


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

# check if the given pid is a running process
def check_pid(pid):        
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def get_all_service_status():
    '''
    Steps
    1. For each service
        - ssh to server
        - check pid is running
        - check if error.txt is empty
        - send message based on it
    '''

    statuses = []
    for service in services:
        ssh_client = SSH(host=service['server_url'])

        pid = service['process_id']
        exit_status = ssh_client.execute_exit_status(
                        'ps -p {0}'.format(pid))
        if exit_status:
            statuses.append('{0} - {1} - {2} - {3}'.format(
                service['repo_url'],
                service['server_name'],
                service['process_id'],
                'Service is not running anymore.'))

        else:
            statuses.append('{0} - {1} - {2} - {3}'.format(
                service['repo_url'],
                service['server_name'],
                service['process_id'],
                'Service is running.'))

        std_out, _ = ssh_client.execute('cat {0}'.format(
                        service['log_path'] + '/error.txt'))

        if std_out:
            statuses[-1] += ' There were some errors. \n```' + std_out + '```'
        else:
            statuses[-1] += ''

        ssh_client.close()

    if not statuses:
        statuses.append('There are no services running at this time.')
    return '\n'.join(statuses)

def clear_completed_services():
    global services

    new_services = []
    for i, service in enumerate(services):
    
        ssh_client = SSH(host=service['server_url'])
        
        pid = service['process_id']
        exit_status = ssh_client.execute_exit_status(
                        'ps -p {0}'.format(pid))

        if not exit_status:
            new_services.append(service)

        ssh_client.close()
             
    services = new_services
    pickle.dump(services, open('services.pkl', 'wb'))


def main():
    ssh = SSH()
    print ssh.execute('ls')
    ssh.close()

if __name__ == '__main__':
    main()
