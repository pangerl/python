import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from utils import not_hidden, rename, put, mkdir, delete, delete_dir, down
from config import host, port, username, key, local_dir
from ParamikoClient import ParamikoClient


# 封装的一个MyHandler类
class MyHandler(FileSystemEventHandler):

    # 初始化传入一个sftp对象
    def __init__(self, sftp):
        self.sftp = sftp

    # 文件变化
    def on_modified(self, event):
        if not_hidden(event.src_path):
            if not event.is_directory:
                self.on_created(event)

    # 文件改名
    def on_moved(self, event):
        rename(self.sftp, event.src_path, event.dest_path)

    # 创建文件
    def on_created(self, event):
        if not_hidden(event.src_path):
            if not event.is_directory:
                put(self.sftp, event.src_path)
            else:
                mkdir(self.sftp, event.src_path)

    # 删除文件
    def on_deleted(self, event):
        if not event.is_directory:
            delete(self.sftp, event.src_path)
        else:
            delete_dir(self.sftp, event.src_path)


def main():
    # 实例化一个ParamikoClient类,用于连接
    client = ParamikoClient(host, port, username, key)
    sftp = client.sftp
    # 先全量下载一遍
    down(sftp)

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
