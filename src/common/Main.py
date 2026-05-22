# MIT License
#
# Copyright (c) 2026 Toyohiko Komatsu (dragonkomat)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# -*- coding: utf-8 -*-

import argparse
import logging
from pathlib import Path
from ruamel.yaml import YAML

from common import Common

from report import DcrJmaEarthquakeEarlyWarning
from report import DcxNullMsg
from azarashi.qzss_dcr_lib.report.qzss_dc_report import *

DEFAULT_CONFPATH = "/etc/qzssdcragent/config.yaml"
DEFAULT_CACHEPATH = "/var/cache/qzssdcragent_cache.bin"
DEFAULT_LOGLEVEL = "INFO"

class Main:
    def check_args(self):
        """
        コマンドライン引数の解析
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-c","--config-file",action="store",dest="config_file",default=DEFAULT_CONFPATH)
        parser.add_argument("-s","--cache-file",action="store",dest="cache_file",default=DEFAULT_CACHEPATH)
        parser.add_argument("-l","--log-level",action="store",dest="log_level",default=DEFAULT_LOGLEVEL)
        parser.add_argument("-t","--test-only",action="store_true",dest="test_only",default=False)
        parser.add_argument("-x","--noload-cache",action="store_true",dest="noload_cache",default=False)
        parser.add_argument("-y","--nodump-cache",action="store_true",dest="nodump_cache",default=False)
        self.common.args = parser.parse_args()

    def init_log(self):
        """
        ログ出力の初期化
        """
        log = logging.getLogger('log')
        log_handler = logging.StreamHandler()   # sys.stderr
        log_formatter = logging.Formatter('%(levelname)s: %(message)s')
        log_handler.setFormatter(log_formatter)
        log.addHandler(log_handler)
        log.setLevel(self.common.args.log_level)
        self.common.log = log

    def init_reports(self):
        """
        レポート処理テーブルの初期化
        """
        self.reports = {
            QzssDcReportJmaEarthquakeEarlyWarning: DcrJmaEarthquakeEarlyWarning(self.common),
            QzssDcxNullMsg: DcxNullMsg(self.common)
        }

    def check_configs(self):
        """
        設定ファイルのロードと確認
        """
        yaml = YAML(typ="safe", pure=True)
        config = yaml.load(Path(self.common.args.config_file))

        self.common.check_config(config)

        conf_report = config["Report"]
        conf_report_default = conf_report["Default"]
        for key in self.reports.keys():

            conf_report_sub = conf_report[key.__name__]
            if conf_report_sub is None:
                conf_report_sub = dict(conf_report_default)
            else:
                conf_report_sub = { **conf_report_default, **conf_report_sub }

            self.reports[key].check(key, conf_report_sub)

    def __init__(self):
        """
        Mainインスタンスの初期化
        """
        self.common = Common()
        self.check_args()
        self.init_log()
        self.init_reports()
        self.check_configs()

    def start(self):
        """
        メインループの開始
        """
        pass
