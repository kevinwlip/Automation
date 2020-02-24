#!/usr/bin/python

import os
from .zbSSH import Shell, CLI

# sync pcaps from AWS
def syncAWS(TG_HOST, TG_PORT, TG_UNAME, TG_PWD):
    kwargs = {}
    kwargs['hostname'] = TG_HOST
    kwargs['username'] = TG_UNAME
    kwargs['password'] = TG_PWD
    kwargs['port'] = TG_PORT
    repo = S3(**kwargs)
    print((repo.syncDownload("pcaps/", "", False, False)))
    repo.closeSSH()



class S3():
    def __init__(self, **kwargs):
        #self.ssh = Shell(**kwargs)
        self.ssh = CLI(**kwargs)


    def uploadFile(self, localFile, remoteBucket):
        cmd = "aws s3 cp "+filename+" s3://zbat/pcaps/"+remoteBucket
        output, err = self.ssh.runCommand(cmd)
        
        if err:
            print (err)
            return False
        else:
            return output


    def removeFile(self, remoteBucket):
        cmd = "aws s3 rm s3://zbat/pcaps/"+remoteBucket
        output, err = self.ssh.runCommand(cmd)
        
        if err:
            print (err)
            return False
        else:
            return output


    def removeDir(self, dirname):
        cmd = "aws s3 rm s3://zbat/pcaps/"+dirname+" --recursive"
        output, err = self.ssh.runCommand(cmd)
        
        if err:
            print (err)
            return False
        else:
            return output


    def syncUpload(self, localDir, remoteBucket, delete=False, localToSsh=False):
        if localToSsh:
            idx = localDir.find("pcaps")
            sshDir = localDir[idx:]
            cmd = "sshpass -p '"+self.ssh.password+"' scp -P "+str(self.ssh.port)+" -r "+localDir + " "+self.ssh.username+"@"+self.ssh.hostname+":"
            os.system(cmd)
        else:
            sshDir = localDir

        cmd = "aws s3 sync "+sshDir+"/ s3://zbat/pcaps/"+remoteBucket
        if delete:
            cmd += " --delete"
        output, err = self.ssh.runCommand(cmd)
        
        if err:
            print (err)
            return False
        else:
            return output


    def syncDownload(self, localDir, remoteBucket, delete=False, sshToLocal=False):
        # create localDir if not existed
        output, err = self.ssh.runCommand("mkdir -p {}".format(localDir))
        
        if sshToLocal:
            idx = localDir.find("pcaps")
            sshDir = localDir[idx:]
            cmd = "aws s3 sync s3://zbat/pcaps/"+remoteBucket+" "+sshDir
            if delete:
                cmd += " --delete"
            output, err = self.ssh.runCommand(cmd)
            
            if err:
                print (err)
                return False
            else:
                cmd = "sshpass -p '"+self.ssh.password+"' scp -P "+str(self.ssh.port)+" -r "+self.ssh.username+"@"+self.ssh.hostname+":"+sshDir+" "+localDir
                os.system(cmd)
                return output
        else:
            cmd = "aws s3 sync s3://zbat/pcaps/"+remoteBucket+" "+localDir
            if delete:
                cmd += " --delete"
            output, err = self.ssh.runCommand(cmd)
            
            if err:
                print (err)
                return False
            else:
                return output


    def show(self, remoteBucket):
        cmd = "aws s3 ls s3://zbat/pcaps/"+remoteBucket
        output, err = self.ssh.runCommand(cmd)
        
        if err:
            print (err)
            return False
        else:
            return output

    def closeSSH(self):
        self.ssh.close()


# test
'''
HOST = 'XX.XX.XX.XX'
USERNAME = 'XXXXX'
PASSWORD = 'XXXXX'

kwargs = {}
kwargs['hostname'] = HOST
kwargs['username'] = USERNAME
kwargs['password'] = PASSWORD
repo = S3(**kwargs)

print (repo.syncUpload("pcaps/", "", True, False))
'''
