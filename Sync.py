import paramiko
from scp import SCPClient
import os
import zipfile
import json

def doSync(zipFileLoc,SSHDetail):
    newZip = zipfile.ZipFile(zipFileLoc,mode = 'w')
    try:
        addFile(newZip, SSHDetail['sourceDir'],len(SSHDetail['sourceDir']))
        print ("All compression succeed, closing file")
        newZip.close()
        upload_file(zipFileLoc,SSHDetail)
    except Exception:
        print("Difficulty encounter, closing file \n**The compression might not be completed as it was expected**")
        newZip.close()

def upload_file(sourceFile,SSHDetail):        
    host = SSHDetail['host']  #Server ip address
    port = SSHDetail['port']  # port
    username = SSHDetail['username']  # ssh userID
    password = SSHDetail['password']  # password
    destDir = SSHDetail['destDir']

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    print("opening connection to %s\nClaiming user %s" %(host,username))
    ssh_client.connect(host, port, username, password)
    scpclient = SCPClient(ssh_client.get_transport(),socket_timeout=15.0)

    try:
        print("uploading file to %s" %destDir)
        scpclient.put(sourceFile, destDir)
    except FileNotFoundError as e:
        print(e)
        print("File not found: %s" %sourceFile)
    else:
        print("upload Successful")
    ssh_client.close()



def addFile(newZip, sourceLoc,lengthBaseRoot):
    allFile = os.listdir(sourceLoc)
    for i in allFile:
        if i != "newZip.zip":#do not add itself to zip
            
            if os.path.isdir(os.path.join(sourceLoc, i)):#if is a directory, go recursive
                addFile(newZip, os.path.join(sourceLoc, i),lengthBaseRoot)
            else:
                print("compressing %s" %i) 
                absPath = os.path.join(sourceLoc,i)# current file path in system directory
                #put in zip file with proper sub directory, pop unrelated system file path
                newZip.write(os.path.join(sourceLoc,i),absPath[lengthBaseRoot:len(os.path.join(sourceLoc,i))],zipfile.ZIP_DEFLATED)



with open ("C:\\Users\\Raymond\\Documents\\Sync Script\\SSH.json")as SSHConfig:
    SSHDetail = json.load(SSHConfig)
print(SSHDetail['sourceDir'])

zipName = input("Please Enter your desired zipfile name: ")

doSync(SSHDetail['sourceDir'] + "\\" +zipName + ".zip",SSHDetail)
