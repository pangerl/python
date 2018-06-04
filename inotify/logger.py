# -*- coding: utf-8 -*-
import logging


# 封装了日志的类
class Logger():

    def __init__(self, name):
        # 创建一个logger实例
        self._logger = logging.getLogger(name)
        # 指定最低输出级别
        self._logger.setLevel(logging.DEBUG)
        # 创建一个StreamHandler
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARN)
        # 创建一个FileHandler
        # 指定日志文件目录
        log_path = './logging.log'
        ch2 = logging.FileHandler(log_path)
        ch2.setLevel(logging.INFO)
        # 设置日志输出格式
        formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        ch.setFormatter(formatter)
        ch2.setFormatter(formatter)

        self._logger.addHandler(ch)
        self._logger.addHandler(ch2)

    # 返回一个logger对象
    @property
    def logger(self):
        return self._logger

# logger.debug('debug message')
# logger.info('info message')
# logger.warn('warn message')
# logger.error('error message')
# logger.critical('critical message')
