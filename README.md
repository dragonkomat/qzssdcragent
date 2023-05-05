qzssdcragent (災害・危機管理通報受信エージェント)
=

概要
-
このプログラムでは、みちびきから送信される「災害・危機管理通報」をGNSSモジュールで受信し、ファイル蓄積やメール送信を行います。

必要なハードウェア
-
* 実行環境 (Raspberry pi 等)
* **L1Sの受信に対応した**GNSSモジュール (u-blox MAX-M10S 等)
* その他、接続ケーブルやGNSSアンテナ 等

**※現時点ではu-bloxモジュールのみ対応**

必要なソフトウェア
-
* Ubuntu 22.04 LTS (動作確認済みのバージョン)
* gpsd
* gpsd-clients
* gpsd-tools
* python3 (3.10.6で動作確認済み)
* pip3
* (pip) azarashi

(作成中)