# Google Colab で MiniMax H3（動画）を動かす

[English](README.md)

YouTube チャンネル **AI is in Wonderland** の動画で使ったノートブックとファイルです。Google Colab の GPU（G4 か A100）で ComfyUI を動かし、MiniMax H3（動画）で「最初の絵＋声＋プロンプト」から口の動きが声に合ったカットを作って、Google ドライブに保存します。

## ファイル
| ファイル | 中身 |
|---|---|
| `colab_minimax_h3_v15.ipynb` | ノートブック（セル 0〜6・9）。上から1つずつ動かします。 |
| `workflows/h3_t2v_minimal_864x480.json` | 小さなテスト：文字だけ・5秒・864×480・4ステップ |
| `workflows/h3_i2v_lipsync_1536x864.json` | 最初の絵＋声（口の動きを声に合わせる）・1536×864・4ステップ |
| `h3_job_patch.py` | カットのフォルダ（start.png・voice.wav・prompt.txt）をワークフローにする |
| `sample/c01/` | 見本のカット1つ（この見本のために作ったオリジナルのキャラクター） |
| `auto_cell.py` | ひとまとまりのプログラム：Colab のセル1つに貼って ▶ を1回押すだけで、準備・全カットの生成・ドライブへの保存・ランタイムの停止まで自動で進みます。 |

## 使い方（セルを1つずつ）
1. Colab：「ランタイム」→「ランタイムのタイプを変更」→ **G4**（または A100）。T4・L4 はメモリが足りません。
2. セル0 → 5 を1つずつ動かします。セル5 に出る URL はコピーして、新しいタブのアドレス欄に貼って開きます（クリックでは開けません）。
3. ComfyUI で `test_t2v_5s` を一度実行します。次にセル6 を動かし、ComfyUI の画面を再読み込み（F5）して、`sample_c01` を開いて実行します。
4. 自分のカット：`マイドライブ/AI_Colab/H3/inputs/<好きな名前>/<カット>/` に `start.png`・`voice.wav`・`prompt.txt` を入れ、セル6 の `SET` を書き換えます。
5. 使い終わったら、最後のセルで**必ずランタイムを止めます**（つないでいる間はコンピューティング ユニットが減ります）。

## ひとまとまりのプログラム（`auto_cell.py`）
上の流れが分かったら、セル1つで全部できます。
1. カットのフォルダを `マイドライブ/AI_Colab/H3/inputs/<好きな名前>/c01, c02, …` に入れます（それぞれに `start.png`・`voice.wav`・`prompt.txt`）。フォルダの名前は c01・c02 のように数字を2けたにすると順番が崩れません。
2. Colab：「ランタイムのタイプを変更」→ **G4**（または A100）。
3. `auto_cell.py` をセル1つに貼り、`SET = 'sample'` を自分のフォルダの名前に書き換えて ▶ を押し、ドライブの許可を押します。
4. ComfyUI と PyTorch を入れ、モデル4本を取ってきて、カットを1本ずつ作り、できるたびに `マイドライブ/AI_Colab/H3/output/<日付_時刻>_auto/` に保存します。進み具合はそこの `_STATUS.txt` に書かれます。
5. 全部終わった時（または `MAX_MIN` の90分を過ぎた時、エラーの時）は、**ランタイムを自動で止めます**。途中で止まったら、もう一度押せば続きから作ります（できたカットは飛ばします）。

## ライセンスについての注意（使う前に必ずお読みください）
このリポジトリにはモデルの重みは入っていません。ノートブックが Hugging Face から取ってきます。モデルにはそれぞれのライセンスがあります。ここに書くのは注意点のまとめで、法律の助言ではありません。原文を必ずご自身で確かめてください。
- **MiniMax H3** は **MiniMax H3 Community License Agreement**（オープンソースのライセンスではありません）です：https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE
  - ライセンスが及ぶのは「Applicable Territory」＝世界のうち、**EU・英国・韓国・米国を除いた地域**だけです。その外でモデル・作ったもの・出力を使うことは、このライセンスでは認められていません。
  - 年間の売上が2,000万米ドルを超える商用の製品・サービスは、MiniMax の書面による別の許可が必要です。
  - 利用規定（Acceptable Use Policy）や、使った製品・サービスに「MiniMax H3」「Powered by MiniMax H3」を表示する決まりなどがあります。全文を確かめてください。
- モデルのファイルは Hugging Face の `Comfy-Org/MiniMax-H3`（ComfyUI 用にまとめ直したもの・ライセンスは MiniMax H3 Community License）と `Kijai/MiniMax-H3-experimental`（同じモデルの int8 版）から取ってきます。どちらも MiniMax H3 のライセンスに従います。
- **MiniMax H3-Image** は別のモデルで、ライセンスも別です。ここでは使っていません。
- **ComfyUI** のライセンスは GPL-3.0 です：https://github.com/Comfy-Org/ComfyUI
- `sample/c01/` はこの見本のために作ったオリジナルのキャラクターです。ノートブックを試すためだけに使ってください。
- H3 で作った動画を公開するときは、MiniMax H3 で生成した AI の映像を含むことを書いておくことをおすすめします。

## そのほか
- H3 は**動画**だけです。
- trycloudflare の URL は人に教えないでください。
