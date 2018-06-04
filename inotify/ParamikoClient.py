import paramiko
from logger import Logger

logger = Logger('ssh').logger


# 一个ssh连接的类，对外提供cmd和sftp方法
class ParamikoClient:
    def __init__(self, host, port, username, key):
        self.host = host
        self.port = port
        self.username = username
        self.pkey = paramiko.RSAKey.from_private_key_file(key)

    @property
    def connect(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.host, self.port, self.username, self.pkey)
            return ssh
        except Exception as e:
            # print(e)
            logger.info(e)

    # sftp有两种连接方法，这里用的transport模块
    @property
    def sftp(self):
        transport = paramiko.Transport((self.host, self.port))
        transport.connect(username=self.username, pkey=self.pkey)
        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp

    # 这里用前面connect的方法。
    # @property
    # def sftp(self):
    #     ssh = self.connect
    #     sftp = ssh.open_sftp()
    #     return sftp

    def runcmd(self, cmd):
        ssh = self.connect
        _, stdout, _ = ssh.exec_command(cmd)
        return stdout.read().decode()
