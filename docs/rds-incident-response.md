# RDS 障害対応 Runbook

## 1. フェイルオーバーの検知と初動
RDS（Multi-AZ）のフェイルオーバーは RDS イベント（failover started / completed）で通知される。
フェイルオーバー後もアプリ側で接続エラーが続く場合は、DNS キャッシュが古いエンドポイントを参照している可能性があるため、アプリケーションの再起動または接続プールのリフレッシュを行う。
完了後は CloudWatch の DatabaseConnections が回復しているかを確認する。

## 2. 接続数の枯渇（too many connections）
max_connections はインスタンスクラスのメモリに応じて自動設定される。
SHOW PROCESSLIST で滞留しているセッションを特定し、アプリの接続リークが疑われる場合はコネクションプールの上限設定を見直す。
恒常的に上限へ張り付いている場合は、RDS Proxy の導入またはインスタンスクラスの変更を起票する。

## 3. スロークエリの調査
slow_query_log を有効化し、long_query_time は 1 秒を基準にする。
Performance Insights で負荷の高い SQL を特定し、EXPLAIN で実行計画を確認する。
インデックス追加で改善が見込める場合は、ピーク時間帯を避けてオンライン DDL で適用する。

## 4. ストレージ逼迫
FreeStorageSpace が 10GB を下回ったら警告、5GB を切ったら緊急対応とする。
一般ログやスロークエリログの肥大化が典型的な原因なので、不要なログテーブルをローテーションする。
ストレージ自動拡張（Storage Auto Scaling）が有効かを確認し、無効なら有効化を検討する。
