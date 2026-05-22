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

from __future__ import annotations
import argparse
import logging
import os
import signal
import sys

from common import Common

DEFAULT_CONFPATH = "/etc/qzssdcragent/config.yaml"
DEFAULT_CACHEPATH = "/var/cache/qzssdcragent_cache.bin"
DEFAULT_LOGLEVEL = "INFO"

class Main:

    def __init__(self):
        """
        Mainインスタンスの初期化
        """
        # stdout/stderrを行バッファモードにする
        sys.stdout = os.fdopen(sys.stdout.fileno(), "w", buffering=1)
        sys.stderr = os.fdopen(sys.stderr.fileno(), "w", buffering=1)

        # 各種初期化
        self.args = self.check_args()
        self.log = self.init_log()

        # Commonオブジェクトの生成
        self.common = Common(self.args, self.log)

        # シグナルハンドラの登録
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def check_args(self) -> argparse.Namespace:
        """
        コマンドライン引数の解析
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-c","--config-file",action="store",dest="config_file",default=DEFAULT_CONFPATH)
        parser.add_argument("-s","--cache-file",action="store",dest="cache_file",default=DEFAULT_CACHEPATH)
        parser.add_argument("-l","--log-level",action="store",dest="log_level",default=DEFAULT_LOGLEVEL)
        parser.add_argument("-t","--test-only",action="store_true",dest="test_only",default=False)
        parser.add_argument("-x","--noload-cache",action="store_true",dest="noload_cache",default=False)
        parser.add_argument("-y","--nosave-cache",action="store_true",dest="nosave_cache",default=False)
        return parser.parse_args()

    def init_log(self) -> logging.Logger:
        """
        ログ出力の初期化
        """
        assert self.args is not None

        log = logging.getLogger('log')
        log_handler = logging.StreamHandler()   # sys.stderr
        log_formatter = logging.Formatter('%(levelname)s: %(message)s')
        log_handler.setFormatter(log_formatter)
        log.addHandler(log_handler)
        log.setLevel(self.args.log_level)
        return log

    def signal_handler(self, signum, frame):
        """
        シグナルハンドラ
        """
        self.common.signal_handler(signum, frame)
        sys.exit(0)

    def start(self):
        """
        メイン処理開始
        """
        self.common.start()
        