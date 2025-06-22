# [Q-Assist™ subprint to card](https://github.com/katsuma-inoue-42/qassist_to_card)

[Q-Assist™](https://medilink-study.com/)のサブプリントを自動的に分割してデッキ化するPythonソフトウェアです。
[Anki](https://apps.ankiweb.net/)での使用を想定し、デッキをロードするためのCSVファイル (表ファイル)も同時に生成します。
家庭内で依頼されて作成したものを、個人学習の効率化の目的の下、MITライセンスで一般公開しています。
この[リンク](http://colab.research.google.com/github/katsuma-inoue-42/qassist_to_card/blob/master/qassist_to_card.ipynb)からアクセス下さい（規約ならびに詳細な使い方は全てこの中に記載されています）。

## 主な機能・特徴
- 穴埋め&解答PDFから自動的に穴埋め箇所を抽出し、Ankiデッキ用の画像と対応するCSVファイルを作成します。
- Google Colaboratory™上で動作するため、Pythonの環境構築は不要で、Google Drive™上にアップロードされたPDFを指定するだけで、Ankiデッキを生成できます。
- 一単元あたりおよそ数十秒〜数分でデッキを生成可能でき、Zipファイルの形でまとめてダウンロードできます。
- 単元名や章・節、ページ数などの情報も抽出されCSVファイルに保存されるため、テンプレートを調整してデッキのデザインを自由に調整できます（下記画像を実現するテンプレートの例も[リンク](http://colab.research.google.com/github/katsuma-inoue-42/qassist_to_card/blob/master/qassist_to_card.ipynb)先に記載されています）。

![blank](https://raw.githubusercontent.com/katsuma-inoue-42/qassist_to_card/refs/heads/master/docs/assets/blank.png)
![answer](https://raw.githubusercontent.com/katsuma-inoue-42/qassist_to_card/refs/heads/master/docs/assets/answer.png)
