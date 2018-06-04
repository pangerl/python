import os
import stat
from config import remote_dir, local_dir
from logger import Logger

logger = Logger('inotify').logger


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


def down(sftp):
    all_files, all_dirs = walk(sftp, remote_dir)
    all_files = filter(not_hidden, all_files)
    all_dirs = filter(not_hidden, all_dirs)
    for dirs in all_dirs:
        os.makedirs(os.path.join(local_dir,
                    os.path.relpath(dirs, remote_dir)), exist_ok=True)
    for file_path in all_files:
        sftp.get(file_path, os.path.join(local_dir,
                 os.path.relpath(file_path, remote_dir)))
    # print('全量下载完成')
    logger.info('全量下载完成')


def not_hidden(path):
    if os.path.basename(path).startswith('.'):
        return False
    else:
        return True


def put(sftp, path):
    sftp.put(path, os.path.join(remote_dir,
             os.path.relpath(path, local_dir)))
    # print('更新 {} 成功！'.format(os.path.basename(path)))
    logger.info('更新 {} 成功！'.format(os.path.basename(path)))


def delete(sftp, path):
    sftp.remove(os.path.join(remote_dir,
                os.path.relpath(path, local_dir)))
    # print('删除 {} 成功！'.format(os.path.basename(path)))
    logger.info('删除 {} 成功！'.format(os.path.basename(path)))


def delete_dir(sftp, path):
    sftp.rmdir(os.path.join(remote_dir,
               os.path.relpath(path, local_dir)))
    # print('删除 {} 成功！'.format(os.path.basename(path)))
    logger.info('删除 {} 成功！'.format(os.path.basename(path)))


def rename(sftp, src_path, dest_path):
    path_new = os.path.join(remote_dir,
                            os.path.relpath(src_path, local_dir))
    path_old = os.path.join(remote_dir,
                            os.path.relpath(dest_path, local_dir))
    sftp.rename(path_new, path_old)
    # print('{} 改名为 {}'.format(os.path.basename(src_path),
    #       os.path.basename(dest_path)))
    logger.info('{} 改名为 {}'.format(os.path.basename(src_path),
                os.path.basename(dest_path)))


def mkdir(sftp, path):
    sftp.mkdir(os.path.join(remote_dir,
               os.path.relpath(path, local_dir)))
    # print('创建{}文件夹'.format(os.path.basename(path)))
    logger.info('创建{}文件夹'.format(os.path.basename(path)))
