import time
import paramiko
import os
import stat
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 配置路径
remote_dir = '/application/nginx/conf/conf.d'
local_dir = '/Users/huangxiaojun/Desktop/123'


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
            print(e)

    @property
    def sftp(self):
        transport = paramiko.Transport((self.host, self.port))
        transport.connect(username=self.username, pkey=self.pkey)
        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp

    def runcmd(self, cmd):
        ssh = self.connect
        _, stdout, _ = ssh.exec_command(cmd)
        return stdout.read().decode()


def walk(sftp, path):
    all_files = []
    all_dirs = []
    files = sftp.listdir_attr(path)
    for f in files:
        filename = path + '/' + f.filename
        if stat.S_ISDIR(f.st_mode):
            file_list, dir_list = walk(sftp, filename)
            all_files.extend(file_list)
            all_dirs.extend(dir_list)
            all_dirs.append(filename)
        else:
            all_files.append(filename)
    return all_files, all_dirs


def down(sftp, remote_dir, local_dir):
    all_files, all_dirs = walk(sftp, remote_dir)
    all_files = filter(not_hidden, all_files)
    all_dirs = filter(not_hidden, all_dirs)
    for dirs in all_dirs:
        os.makedirs(os.path.join(local_dir,
                    os.path.relpath(dirs, remote_dir)), exist_ok=True)
    for file_path in all_files:
        sftp.get(file_path, os.path.join(local_dir,
                 os.path.relpath(file_path, remote_dir)))
    print('全量下载完成')


def not_hidden(path):
    if os.path.basename(path).startswith('.'):
        return False
    else:
        return True


def put(sftp, path):
    sftp.put(path, os.path.join(remote_dir,
             os.path.relpath(path, local_dir)))
    print('更新 {} 成功！'.format(os.path.basename(path)))


def delete(sftp, path):
    sftp.remove(os.path.join(remote_dir,
                os.path.relpath(path, local_dir)))
    print('删除 {} 成功！'.format(os.path.basename(path)))


def delete_dir(sftp, path):
    sftp.rmdir(os.path.join(remote_dir,
               os.path.relpath(path, local_dir)))
    print('删除 {} 成功！'.format(os.path.basename(path)))


def rename(sftp, src_path, dest_path):
    path_new = os.path.join(remote_dir,
                            os.path.relpath(src_path, local_dir))
    path_old = os.path.join(remote_dir,
                            os.path.relpath(dest_path, local_dir))
    sftp.rename(path_new, path_old)
    print('{} 改名为 {}'.format(os.path.basename(src_path),
          os.path.basename(dest_path)))


def mkdir(sftp, path):
    sftp.mkdir(os.path.join(remote_dir,
               os.path.relpath(path, local_dir)))
    print('创建{}文件夹'.format(os.path.basename(path)))


class MyHandler(FileSystemEventHandler):

    def __init__(self, sftp):
        self.sftp = sftp

    def on_modified(self, event):
        if not_hidden(event.src_path):
            if not event.is_directory:
                self.on_created(event)

    def on_moved(self, event):
        rename(self.sftp, event.src_path, event.dest_path)

    def on_created(self, event):
        if not_hidden(event.src_path):
            if not event.is_directory:
                put(self.sftp, event.src_path)
            else:
                mkdir(self.sftp, event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            delete(self.sftp, event.src_path)
        else:
            delete_dir(self.sftp, event.src_path)


def main():
    host = '172.31.101.38'
    port = 22
    username = 'root'
    key = '/Users/huangxiaojun/.ssh/id_rsa'

    # if remote_dir[-1] == '/':
    #     remote_dir = remote_dir[0:-1]
    # if local_dir[-1] == '/':
    #     remote_dir = remote_dir[0:-1]

    client = ParamikoClient(host, port, username, key)
    sftp = client.sftp
    down(sftp, remote_dir, local_dir)

    event_handler = MyHandler(sftp)
    observer = Observer()
    observer.schedule(event_handler, path=local_dir, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
