import threading
import paramiko
import socket
import time
class SSHThread(threading.Thread):
    def __init__(self, parent ,log):
        threading.Thread.__init__(self)
        self.parent = parent
        self.log = log
        self.isConnected = False
        self._stop_ = threading.Event()

    def run(self):
        if not self.parent.sshClient.isActive():
            try:
                # Create an SSH client and attempt to connect
                self.log.print(f"connecting to {self.parent.sshClient.username}@{self.parent.sshClient.host}")
                self.parent.sshClient.connect()
                self.isConnected = self.parent.sshClient.isActive()
                if (self.isConnected):
                    self.log.print(f"Successfully Connected to {self.parent.sshClient.username}@{self.parent.sshClient.host}")

                while self.isConnected:
                    if not self.parent.sshClient.isActive():
                        self.isConnected = False
                        self.log.print("Connection disconnected!")
                        self.parent._unExpectedDisconnect_()
                    elif(self._stop_.is_set()):

                        self.parent.sshClient.disconnect()

                        self.isConnected = False
                        #self.log.print("Stop signaled!")
                    else:
                        time.sleep(1)



            except paramiko.ssh_exception.SSHException as e:
                self.log.print(str(e))
            except socket.error as e:
                self.log.print(f"Socket error:{str(e)}")
            except Exception as e:
                self.log.print(f"ExpectionT:{str(e)}")

        else:
            self.log.print(f"Connection to {self.parent.sshClient.username}@{self.parent.sshClient.host} already established!")

    def stop(self):
        self._stop_.set()