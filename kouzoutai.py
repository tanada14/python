#!/usr/bin/python
### -*- coding: utf-8 -*-
###
### 構造体のようなクラスの使用例
###

from __future__ import print_function
import re, logging, sys

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("ESE_struct")
logger.setLevel(logging.DEBUG)


class ESE_struct:
    '''v1, v2, v3 というメンバを持つ
'''
    
    def __init__(self, v1=None, v2=None, v3=None, line=None):
        '''メンバの値を設定する
'''
        if line is None:
            assert v1 is not None and v2 is not None and v3 is not None, "invalid arguments={}".format( (v1, v2, v3) )
        else:
            ## スペースで区切られた3つの要素 (整数 整数 文字列) からメンバの値を設定する
            m = re.match("^(\d+)\s+(\d+)\s+(\w+).*$", line)
            assert m is not None, "invalid line={}".format(line)
            v1, v2, v3 = m.groups()
            
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

    def __str__(self):
        '''str() 関数の引数として与えられた場合に返される文字列
'''
        retval = "v1={0} v2={1} v3={2}".format(self.v1, self.v2, self.v3)
        return retval

if __name__ == "__main__":
    cont = True
    vec = [ ]
    while cont:
        l = None
        try:
            #l = sys.stdin.readline().strip()
            l = "1 2 aaaa"

            if l:
                obj = ESE_struct(line=l)
                print ("line={0} is parsed as:{1}".format(l, obj))
                print ("v1={v1} v2={v2} v3={v3}".format(v1=obj.v1, v2=obj.v2, v3=obj.v3))
                vec.append(obj)
            else:
                print ("finished")
                cont = False
        except AssertionError as e:
            print ("line={0} was not parsed".format(l))
            import traceback
            print ("tracebacks follow")
            traceback.print_exc()

    ## v1 の昇順にソート
    vec.sort(key=lambda ese: ese.v1)
    for v in vec:
        print (v)