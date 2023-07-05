import paramiko
from scp import SCPClient
import os
import zipfile
import json


class Synchronizer:
    def __init__(self, SSHDetail=None):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if SSHDetail is not None:
            self.host = SSHDetail['host']  # Server ip address
            self.port = SSHDetail['port']  # port
            self.username = SSHDetail['username']  # ssh userID
            self.password = SSHDetail['password']  # password
            self.directory = SSHDetail['directory']
        else:
            self.host = None  # Server ip address
            self.port = None  # port
            self.username = None  # ssh userID
            self.password = None  # password
            self.directory = None

    def updateConfig(self, SSHDetail):
        self.host = SSHDetail['host']  # Server ip address
        self.port = SSHDetail['port']  # port
        self.username = SSHDetail['username']  # ssh userID
        self.password = SSHDetail['password']  # password
        self.directory = SSHDetail['directory']

    def doUpload(self,localDir, RemoteDir):#TODO test multiple folder and folder with multiple file
        #localDir = localDir.replace('\\', '\\\\')
        numDir = 0
        numFile = 0
        sftp = self.ssh_client.open_sftp()

        for root, dirs, files in os.walk(localDir):

            for dir in dirs:
                numDir+=1
                remote_dir = os.path.join(RemoteDir, os.path.relpath(os.path.join(root, dir), localDir))
                print(f"makeing directory: {remote_dir}")
                try:
                    sftp.mkdir(remote_dir)
                    print(f"Directory: {remote_dir} created.")
                except IOError:
                    print(f"The directory: {remote_dir} already exist.")

            for file in files:
                numFile+=1
                lPath = os.path.join(root,file)
                rPath = os.path.join(RemoteDir, os.path.relpath(lPath, localDir)).replace('\\', '/')
                print(f"moving file from local {lPath} to {self.username}@{self.host}:{rPath}")
                sftp.put(lPath, rPath)
        sftp.close()
        return((numDir,numFile))

    def doDownload(self,RemoteDir, localDir):
        numDir = 0
        numFile = 0
        sftp = self.ssh_client.open_sftp()
        for entry in sftp.listdir_attr(RemoteDir):
            remote_file = RemoteDir + '/' + entry.filename
            local_file = os.path.join(localDir, entry.filename)
            remote_file = remote_file.replace("//", "/")
            if entry.st_mode & 0o040000:  # If it's a directory
                print(f"making folder{local_file}")
                os.makedirs(local_file, exist_ok=True)
                (newDir, newFile)=self.doDownload(remote_file, local_file)
                numDir += newDir + 1
                numFile += newFile
            else:

                print(f"Pulling {remote_file} from {self.username}@{self.host} to local at {local_file}")
                sftp.get(remote_file, local_file)
                numFile+=1

        sftp.close()
        return((numDir,numFile))


    def __addFile__(self, newZip, sourceLoc, lengthBaseRoot):
        allFile = os.listdir(sourceLoc)
        for i in allFile:
            if i != "newZip.zip":  # do not add itself to zip

                if os.path.isdir(os.path.join(sourceLoc, i)):  # if is a directory, go recursive
                    self.__addFile__(newZip, os.path.join(sourceLoc, i), lengthBaseRoot)
                else:
                    print("compressing %s" % i)
                    absPath = os.path.join(sourceLoc, i)  # current file path in system directory
                    # put in zip file with proper sub directory, pop unrelated system file path
                    newZip.write(os.path.join(sourceLoc, i), absPath[lengthBaseRoot:len(os.path.join(sourceLoc, i))],
                                 zipfile.ZIP_DEFLATED)
    def connect(self):
        self.ssh_client.connect(self.host, username=self.username, password=self.password, allow_agent=True)
    def disconnect(self):
        self.ssh_client.close()

    def runCommand(self, command):
        print("SyncScript: connecting to remote...")
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        for i in [stdout, stderr]:
            output_lines = i.readlines()
            if output_lines:
                for lines in output_lines:
                    print(f"remote: {lines.strip()}")
        print("SyncScript: closing tunnel...")
        self.ssh_client.close()

    def isActive(self):
        transport = self.ssh_client.get_transport()
        return transport is not None and transport.is_active()

def test(a, b):
    return "inprogress"


if __name__ == '__main__':
    with open("C:\\Users\\Raymond\\Documents\\Sync Script\\config.json") as SSHConfig:
        SSHDetail = json.load(SSHConfig)
    print(SSHDetail['sourceDir'])

    zipName = input("Please Enter your desired zipfile name: ")

    Synchronizer.doUpload(SSHDetail['sourceDir'] + "\\" + zipName + ".zip", SSHDetail)
