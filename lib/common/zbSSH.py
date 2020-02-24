#!/usr/bin/python


import time, paramiko, logging, io, pdb

class Shell():
    def __init__(self, **kwargs):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.password = kwargs['password']
        self.username = kwargs['username']
        self.hostname = kwargs['hostname']
        self.port = kwargs['port'] if 'port' in kwargs else 22

        try:
            self.ssh.connect(self.hostname, port=self.port, username=self.username, password=self.password)
        except paramiko.SSHException as err:
            logging.error("Shell failed - {}".format(err))
            return
        logging.info("Shell connected")


    def runCommand(self, cmd):
        try:
            cmd = cmd.strip()
            logging.info("Executing %s" % cmd)
            stdin,stdout,stderr = self.ssh.exec_command(cmd + "\n", get_pty=True, timeout=300)
        except Exception as e:
            logging.error(e)
        output = stdout.read()
        err = stderr.read()
        return output, err

    def putSFTP(self, **kwargs):
        filePath = kwargs['filePath']
        newFilePath = kwargs['newFilePath']
        sftp = self.ssh.open_sftp()
        sftp.put(filePath, newFilePath)
        sftp.close()

    def close(self):
        self.ssh.close()

class CLI():

    def __init__(self, **kwargs):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.password = kwargs['password']
        self.username = kwargs['username']
        self.hostname = kwargs['hostname']
        self.port = kwargs['port'] if 'port' in kwargs else 22
        
        try:
            self.ssh.connect(self.hostname, port=self.port, username=self.username, password=self.password)
        except paramiko.SSHException:
            logging.error("CLI Failed")
            quit()
        logging.info("CLI connected")


    def runCommand(self, cmd, sec=0):
        err = False
        self.chan = self.ssh.get_transport().open_session()
        self.chan.settimeout(0)
        self.chan.invoke_shell()
        self.chan.set_combine_stderr(True)
        self.chan.send_ready()

        try:
            logging.info("Executing %s" % cmd)
            self.chan.send(cmd + "\n")
            contents = io.StringIO()
            error = io.StringIO()
            time.sleep(sec)
            i =0
            while i<60:
                if self.chan.recv_ready():
                    break
                time.sleep(1)
                i+=1
            while self.chan.recv_ready():
                data = self.chan.recv(1024)
                contents.write(data)
        except Exception as err:
            self.logger.error(err)

        self.chan.close()
        output = contents.getvalue()
        return output, err

    def close(self):
        self.ssh.close()