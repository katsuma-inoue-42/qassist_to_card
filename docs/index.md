---
layout: default
title: Q-AssistのサブプリントからAnkiデッキを自動作成
description: Q-Assistのサブプリントから問題を抽出してAnkiデッキ化するPythonソフトウェア
lang: ja_JP
---

# Q-Assist™ subprint to card

**qassist_to_card**は、[Q-Assist™](https://medilink-study.com/)のサブプリントを自動的に分割してデッキ化するPythonソフトウェアです。
[Anki](https://apps.ankiweb.net/)の使用を想定し、カード両面用の画像のみならず、デッキを読み込むためのCSVファイル（表ファイル）も同時に生成します。
元々家庭内で依頼されて作成したもので、個人学習の効率化を目的としてMITライセンス（オープンソース）で一般公開しています。

[このColabリンク](http://colab.research.google.com/github/katsuma-inoue-42/qassist_to_card/blob/master/qassist_to_card.ipynb)にアクセスして、ブラウザ上で操作して使用してください（規約および詳細な使い方はすべてこの中に記載されています）。

## 主な機能・特徴
- 穴埋め&解答PDFから自動的に穴埋め箇所を抽出し、Ankiデッキ用の画像と対応するCSVファイルを作成します。
- Google Colaboratory™上で動作するため、Pythonの環境構築は不要で、ブラウザ上で操作が完結します。
- Googleアカウントを用意し、[Google Drive™](https://drive.google.com/drive/my-drive)上にアップロードされた穴埋め&解答PDFを指定して実行するだけでAnkiデッキを生成できます。
- 一単元あたりおよそ数十秒〜数分でデッキを生成でき、Zipファイルの形でまとめてダウンロードできます。
- 単元名や章・節、ページ数などの情報も抽出されCSVファイルに保存されるため、テンプレートを調整してデッキのデザインを自由に変更できます（下記画像参照。この例を実現するテンプレートのサンプルも[リンク先](http://colab.research.google.com/github/katsuma-inoue-42/qassist_to_card/blob/master/qassist_to_card.ipynb)の末尾に記載されています）。

**Ankiの表面（穴埋め）例:**
![blank](https://raw.githubusercontent.com/katsuma-inoue-42/qassist_to_card/refs/heads/master/docs/assets/blank.png)

**Ankiの裏面（解答）例:**
![answer](https://raw.githubusercontent.com/katsuma-inoue-42/qassist_to_card/refs/heads/master/docs/assets/answer.png)

## 連絡先
なにか不明な点や問題がありましたら、[GitHub Issues](https://github.com/katsuma-inoue-42/qassist_to_card/issues)からお問い合わせください（多忙のため返信に時間を要する場合がありますが予めご了承ください）。
