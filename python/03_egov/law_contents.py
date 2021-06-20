#Linux環境でスクリプトの1行目に記述する、特殊な文字列Shebang.スクリプトを実行するインタープリタを示す。
#!/usr/bin/env python
# デフォルトの文字コードの取得
# coding: utf-8 
#指定した文字コードでファイルを開くことができる。
import codecs
#JSONライブラリは、データ型の変換を意識することなく利用できる。
import json
#関数に影響を及ぼしたり他の関数を返したりする。関数の引数と返り値を保存。
from functools import lru_cache
#データ出力の整然化モジュール
# from pprint import pprint
#Python で文字列の集合を「意味合いをもたせた記号を組み合わせて」表現するモジュール re.
import re
#XML データを解析および作成するモジュール
from xml.etree import ElementTree
#HTTP通信用のPythonのライブラリ
import requests

#関数をメモ化用の呼び出し可能オブジェクトでラップする。
@lru_cache
#getは、辞書型(dict型)のメソッド。raw文字列のdef()内のデータを使って処理する。
def get_raw(ID):
    """
    e-GovAPIから法律IDで指定された法律の内容を取得
    Retrieve contents of the law specified with law ID from e-Gov API.
　　数値を文字列に変換して、複数の引数を組として受け取る。
    Args:
        ID (str): ID of the law, like '12ATV589861'
　　　関数の呼び出し元へ値を返す。raw型の日本語文字列のリストを作成。
        Returns:
        raw (list[str]): raw contents of J-GCP
    """
    #法例APIのurl。f文字列は順番に引数を指定したり名前を決めてキーワード引数で指定したりして置換フィールド{}に値を挿入できる。
    url = f"https://elaws.e-gov.go.jp/api/1/lawdata/{ID}"
    #rの定義。
    r = requests.get(url)
    #XMLから文字列に変換し、インポートしてツリー状の構造を解析する。文字コードはutf-8
    root = ElementTree.fromstring(r.content.decode(encoding="utf-8"))
    #数、文字列、空白は削除,文字列の中に数字が入っていたら、繰り返し処理。
    contents = [e.text.strip() for e in root.iter() if e.text]
#文字列を返す。
    return [t for t in contents if t]

#raw型でGoogleクラウドプラットフォームを利用して前処理。
def preprocess_gcp(raw):
    """
    J-GCPの未加工コンテンツに対して前処理を実行。
    Perform pre-processing on raw contents of J-GCP.
    文字列を組にしたものを受取る。
    Args:
        raw (list[str]): raw contents of J-GCP
    前処理した文字列を返す。
    Returns:
        str: pre-processed string of J-GCP
    
    Notes:
         記事番号は削除。（および）で囲まれた文字列は削除。「と」は削除。
        - Article number will be removed.
        - Strings enclosed with （ and ） will be removed.
        - 「 and 」 will be removed.
    """
    # 文字列の全てを指定。
    # contents = raw[:]
    #記事番号を削除
    # Remove article number
    contents = raw[: raw.index("第number条")]
    #文を選択。
    # Select sentenses
    #文字列の最後が「。」で終わるまでが文。
    contents = [s for s in contents if s.endswith("。")]
    #文を繋げる場合。
    # Join the sentenses
    #文は文字列を連結したもの。
    gcp = "".join(contents)
    #「と」は削除。
    # 「 and 」 will be removed
    #; , : は削除。
    gcp = gcp.translate(str.maketrans({"「": "", "」": ""}))
    # （）で囲まれた文字列を削除。
    return re.sub("（[^（|^）]*）", "", gcp)

#メインの関数
def main():
    #法例IDの文字列を取り出す。
    gcp_raw = get_raw("ID")
    # 文字列は原則として全て整列する。
    # pprint(gcp_raw, compact=False)
    #jsonファイルを作成し、文字列を書き込む。文字コードとインデント指定。ascii文字は無視。
    with codecs.open("gcp_raw.json", "w", encoding="utf-8") as fh:
        json.dump({"gcp": gcp_raw}, fh, indent=4, ensure_ascii=False)
    #文字列は、前処理を行う。
    gcp = preprocess_gcp(gcp_raw)
    #文字列の出力は、文字列。文字コード指定。
    # print(gcp)
    with codecs.open("gcp.txt", "w", encoding="utf-8") as fh:
        fh.write(gcp)

#Pythonファイルが「python ファイル名.py というふうに実行されているかどうか」を判定。
if __name__ == "__main__":
    main()


