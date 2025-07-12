# Kanji Clustering API

漢字のクラスタリングと類似度計算を提供するAPIです。

## デプロイメント

本アプリケーションはHerokuにデプロイされています。

- **アプリ名**: kanji-clustering
- **URL**: https://kanji-clustering.herokuapp.com
- **管理者**: yudukikun5120@gmail.com

### API エンドポイント

- `GET /affinities?character={漢字}&kanji_set={漢字セット}` - 指定された漢字の類似度を取得

### Herokuコマンド

ログ確認:
```bash
heroku logs --tail --app kanji-clustering
```

アプリ一覧:
```bash
heroku apps
```
