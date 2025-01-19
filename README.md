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

必要なソフトウェア
-
* Ubuntu 24.04.1 LTS (動作確認済みのバージョン)
* gpsd
* gpsd-clients
* python3 (3.12.3で動作確認済み)
* python3-pip
* (pip3) azarashi (0.11.0で動作確認済み)
* (pip3) dill

(作成中)