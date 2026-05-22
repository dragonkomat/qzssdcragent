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
from datetime import datetime, timedelta
import io
import os
import subprocess
import sys
import time
from types import SimpleNamespace

from azarashi import decode_stream
from azarashi.qzss_dcr_lib.report.qzss_dc_report import QzssDcxNullMsg
import dill

from inout import *
from item import *
from common import *

class Input(IOBase):

    def __init__(self, common:Common):
        super().__init__(common)
        self.cache:list[InputItem] = []

    def check_config(self, config:SimpleNamespace):
        super().check_config(config)

    def remove_expired_cache(self):
        """
        期限切れキャッシュの削除
        """
        config = self.config

        dtexpire = datetime.now() - timedelta(hours=config.CacheValidPeriodHour)
        while len(self.cache) > 0:
            if self.cache[0].report.timestamp >= dtexpire:
                break
            self.cache.pop(0)

    def save_cache(self):
        """
        キャッシュのセーブ
        """
        common = self.common
        log = common.log
        args = common.args

        if args.nosave_cache:
            log.warning("cache save skipped.")
        else:
            log.info("saving cache...")
            try:
                with open(args.cache_file, "wb") as f:
                    dill.dump(self.cache, f)
                log.info(f"cache save completed. (count={len(self.cache)})")
            except Exception as e:
                log.exception(e)
                log.warning("cache save failed.")
                try:
                    os.remove(args.cache_file)
                except Exception as e:
                    pass

    def load_cache(self):
        """
        キャッシュのロード
        """
        common = self.common
        log = common.log
        args = common.args

        log.info(f"cache file is {args.cache_file}")
        if args.noload_cache:
            log.warning("cache load skipped.")
        else:
            log.info("loading cache...")
            try:
                with open(args.cache_file, "rb") as f:
                    self.cache = dill.load(f)
                log.info(f"cache load completed. (count={len(self.cache)})")
                self.remove_expired_cache()
            except FileNotFoundError as e:
                log.warning("cache file not found.")
            except Exception as e:
                log.exception(e)
                log.warning("cache load failed.")
            if self.cache is None:
                self.cache = []

    def process_report(self, item:InputItem):
        common = self.common
        # log = common.log
        
        common.process_message(item)

    def report_handler(self, report, *callback_args, **callback_kwargs):

        # メッセージ監視スレッドにNoneを送信する
        # message_watcher_queue.put(None)
 
        item = InputItem(report)

        # nullメッセージの場合はキャッシュに蓄積しない
        if isinstance(item.report, QzssDcxNullMsg):
            self.process_report(item)
            return

        # キャッシュの確認と追加、レポートの処理
        found = False
        for obj in self.cache:
            if obj.report == item.report:
                found = True
                break
        if found:
            pass    # キャッシュにある場合は何もしない
        else:
            self.cache.append(item)
            self.process_report(item)

        # 期限切れキャッシュの削除
        self.remove_expired_cache()

    def message_loop(self):
        """
        メッセージループ
        """
        common = self.common
        log = common.log
        config = self.config

        while True:

            log.info("subprocess starting...")

            try:
                
                # gpspipe等のコマンドの実行
                with subprocess.Popen(
                        args=config.Cmdline.split(" ")
                        ,stdout=subprocess.PIPE
                        ,stderr=subprocess.DEVNULL
                        ,bufsize=0
                        ,text=False ) as watchproc:

                    log.info("subprocess started. Wait for receiving messages...")

                    # デコード処理
                    with io.BufferedReader(watchproc.stdout, buffer_size=1) as stream:
                        while True:
                            try:
                                decode_stream(
                                    stream=stream
                                    ,msg_type=config.Type
                                    ,callback=self.report_handler
                                    ,unique=False
                                    ,ignore_dcr=False
                                    ,ignore_dcx=False)
                            except Exception as e:
                                # 例外を起こした場合はdecode_streamのループから抜けてコマンド実行をやり直す
                                log.exception(e)
                                log.warning("decode_stream occurred exception! decode_stream terminated.")
                                break
                
                # コマンド実行を中止する
                watchproc.terminate()

            except Exception as e:
                log.exception(e)
                log.error("subprocess occurred exception! Terminate...")
                sys.exit(3)

            # watch processが終了してしまった場合は5秒待ってから再度実行
            log.warning("subprocess terminated. Retry after 5 seconds...")
            time.sleep(5)
