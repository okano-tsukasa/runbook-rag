# ログ調査手順

## 1. CloudWatch Logs Insights での絞り込み
障害時間帯のアプリログは Logs Insights で調査する。基本形は次のとおり。

```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100
```

役に立った調査クエリは再利用できるよう、運用 Wiki の「調査クエリ集」に必ず保存する。

## 2. ALB アクセスログの調査（Athena）
ALB のアクセスログは S3 に保存され、Athena の alb_logs テーブルで SQL 検索できる。
5xx の集計は target_status_code でグルーピングし、特定ターゲットに偏っていないかを見る。
スキャン量を抑えるため、WHERE 句で必ず日付パーティション（day）を指定する。

## 3. 調査時の注意
ログには個人情報が含まれる可能性があるため、調査結果を Slack に貼る際はマスキングする。
本番 DB への直接クエリによる調査は、リードエンジニアの承認を得たうえで読み取り専用ユーザーで行う。
