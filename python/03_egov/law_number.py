import requests
import xml.etree.ElementTree as ET

#e-Gov 法令API 仕様書
#https://www.e-gov.go.jp/elaws/pdf/houreiapi_shiyosyo.pdf

#法令選択
def lawName2No(KEYWORD, TAG='LawName'):
    url = 'https://elaws.e-gov.go.jp/api/1/lawlists/2'
    r = requests.get(url)
    root = ET.fromstring(r.content.decode(encoding='utf-8'))
    iflag = 0
    for i,e in enumerate(root.getiterator()):
        if TAG==e.tag:  
            iflag = 0
        if KEYWORD==e.text: 
            iflag = 1
        if iflag==1 and e.tag=='LawNo':
            return  str(e.text)

#法令表示・抽出
def lawTextExtractor(KEYWORD, lawnum='all', wordn=0, words=[]):
    if lawnum=='all':
        url = 'https://elaws.e-gov.go.jp/api/1/lawdata/'+lawName2No(KEYWORD)
    else:
        url = 'https://elaws.e-gov.go.jp/api/1/articles;lawNum='+lawName2No(KEYWORD)+';article='+str(lawnum)
    r = requests.get(url)
    if r.status_code!=requests.codes.ok:
        return
    root = ET.fromstring(r.content.decode(encoding='utf-8')) 
    lawstrs = []
    ssentcount = 0
    for i,e in enumerate(root.getiterator()):
        for xtag in ['LawTitle', 'SupplProvisionLabel', 'ArticleCaption', 'ArticleTitle', 'ParagraphNum', 'ItemTitle', 'Sentence']:
            if e.tag==xtag :

                if wordn==1 and xtag=='Sentence':#ワード指定する場合
                    tmpstr = ''
                    for word in words:
                        if str(e.text).find(word)>-1:
                            if tmpstr=='':
                                tmpstr = e.text.replace(word, '●'+word)
                            else:
                                tmpstr = tmpstr.replace(word, '★'+word)
                    if tmpstr!='':
                        lawstrs.append(tmpstr)
                        ssentcount += 1

                else:
                    lawstrs.append(str(e.text))
    if lawstrs==[]:
        pass
    else:
        if lawnum=='all':
            print('●条項号数', ssentcount)
        print('\n'.join(lawstrs))#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import json
from functools import lru_cache
from pprint import pprint
from xml.etree import ElementTree
import requests


@lru_cache
def get_law_dict(category=1):
    """
    Return dictionary of law names and numbers.
    This will be retrieved from e-Gov (https://www.e-gov.go.jp/)

    Args:
        category (int): category number, like 1 (all), 2 (法令), 3 (政令), 4 (省令)

    Returns:
        dict(str, str): dictionary of law names (keys) and numbers (values)
    """
    url = f"https://elaws.e-gov.go.jp/api/1/lawlists/{category}"
    r = requests.get(url)
    root = ElementTree.fromstring(r.content.decode(encoding="utf-8"))
    pprint(
        [
            f"{e.tag=}, {e.text=}" for e in root.iter() if e.tag in set(["LawName", "LawNo"])
        ][:4], compact=False)
    names = [e.text for e in root.iter() if e.tag == "LawName"]
    numbers = [e.text for e in root.iter() if e.tag == "LawNo"]
    return {name: num for (name, num) in zip(names, numbers)}


def get_law_number(keyword, category=1):
    """
    Return the law number.
    This will be retrieved from e-Gov (https://www.e-gov.go.jp/)

    Args:
        keyword (str): keyword of the law name
        category (int): category number, like 1 (all), 2 (法令), 3 (政令), 4 (省令)

    Returns:
        dict(str, str): dictionary of law name (key) and law number (value)
    """
    law_dict = get_law_dict(category=category)
    return {k: v for (k, v) in law_dict.items() if keyword in k}


def main():
    # pprint(get_law_dict(category=2), compact=True)
    with codecs.open("law_dict.json", "w", encoding="utf-8") as fh:
        json.dump(get_law_dict(category=2), fh, indent=4, ensure_ascii=False)
    print(get_law_number("日本国憲法", category=2))
    print(get_law_number("著作権", category=2))
    print(get_law_number("医薬品医療機器", category=2))
    print(get_law_number("医薬品の臨床試験", category=4))


if __name__ == "__main__":
    main()
