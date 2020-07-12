# -*- coding: utf-8 -*-
# @Time    : 2020/7/10
# @Author  : 张浩天
# @FileName: ConfigProvider.py
# @Description: 读取LianJiaConfig配置
import os
import configparser
import logging


class ConfigProvider:
    def __init__(self, file):
        if os.path.exists(os.path.join(os.getcwd(), file)):
            self.config = configparser.ConfigParser()
            self.config.read(os.path.join(os.getcwd(), file), encoding="utf-8")
        else:
            logging.error('配置文件不存在!')

    def get(self, cfg, key):
        return self.config.get(cfg, key)

    def set(self, cfg, key, value):
        return self.config.set(cfg, key, value)
