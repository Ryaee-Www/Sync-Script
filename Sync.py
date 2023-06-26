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

    def doUpload(self,localDir, RemoteDir):#TODO solve file path incorrect
        localDir = localDir.replace('\\', '\\\\')
        sftp = self.ssh_client.open_sftp()
        for root, dirs, files in os.walk(localDir):
            for file in files:
                print(file)
                sftp.put(file, RemoteDir)
        #for root, dirs, files in os.walk(localDir):
            #remote_root = RemoteDir + root.replace(localDir, '').replace('\\', '/')
            #for directory in dirs:
                #remote_directory = os.path.join(remote_root, directory)
                #sftp.mkdir(remote_directory)
            #for file in files:
                #local_path = os.path.join(root, file)
                #remote_path = os.path.join(remote_root, file)
                #sftp.put(local_path, remote_path)

        #newZip = zipfile.ZipFile(zipFileLoc, mode='w')
        #try:
            #self.__addFile__(newZip, SSHDetail['sourceDir'], len(SSHDetail['sourceDir']))
            #print("All compression succeed, closing file")
            #newZip.close()
            #self.__uploadFile__(zipFileLoc)
        #except Exception:
            #print("Difficulty encounter, closing file \n**The compression might not be completed as it was expected**")
            #newZip.close()

    def __uploadFile__(self, sourceFile):

        print("opening connection to %s\nClaiming user %s" % (self.host, self.username))
        self.ssh_client.connect(self.host, self.port, self.username, self.password)
        scpclient = SCPClient(self.ssh_client.get_transport(), socket_timeout=15.0)

        try:
            print("uploading file to %s" % self.destDir)
            scpclient.put(sourceFile, self.destDir)
        except FileNotFoundError as e:
            print(e)
            print("File not found: %s" % sourceFile)
        else:
            print("upload Successful")
        self.ssh_client.close()

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

def test(a, b):
    return "inprogress"


if __name__ == '__main__':
    with open("C:\\Users\\Raymond\\Documents\\Sync Script\\config.json") as SSHConfig:
        SSHDetail = json.load(SSHConfig)
    print(SSHDetail['sourceDir'])

    zipName = input("Please Enter your desired zipfile name: ")

    Synchronizer.doUpload(SSHDetail['sourceDir'] + "\\" + zipName + ".zip", SSHDetail)
