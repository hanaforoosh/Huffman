import sys
from collections import Counter
from heapq import *
from copy import deepcopy
import math
import re
import pickle


class tree:
    def __init__(self,label:str = ''):
        self.left  = None
        self.right = None
        self.label = label
        self.bits =''
        self.parent =None

    def merge(self,node1,node2):
        self.label = node1.label+node2.label
        self.left  = node1
        self.right = node2
        node1.parent = self
        node2.parent = self

    def leaves(self):
        ans1=[]
        ans2=[]
        if self.left==None and self.right==None:
            return [self]
        if self.left !=None:
            self.left.bits=self.bits+'0'
            ans1=self.left.leaves()
        if self.right !=None:
            self.right.bits=self.bits+'1'
            ans2=self.right.leaves()
        return [*ans1,*ans2]



class hufftree:
    def __init__(self,arr:list):
        self.arr =  [ (k,v,tree(v)) for (k,v) in arr]
        self.head = tree()
        heapify(self.arr)


    def run_huffman_algorithm(self):
        while(len(self.arr)>1):
            a = heappop(self.arr)
            b = heappop(self.arr)
            self.head.merge(a[2],b[2])
            heappush(self.arr,(a[0]+b[0],a[1]+b[1],deepcopy(self.head)))
            self.head=tree()

        self.head = heappop(self.arr)[2]
    def get_bits(self):
        leaves = self.head.leaves()
        bits =[(leaf.label, leaf.bits) for leaf in leaves]
        return bits

def help():
    print('Usage: python3 huffman.py [OPTION]... [FILE]')
    print('huffman compresseion for text files.\n')

    print('with no OPTION compress the .txt file ,and decompress .huf and .dhf files.\n')
    print('  -c,    --comp                  compress the file')
    print('  -d,    --decomp                decompress the file')
    print(' -dc,    --default-compress      compress the file with the default table')
    print(' -dd,    --default-decompress    decompress the file with the default table')
    print('  -m,    --maketable             make the default table')

def remove_extension(string,ext):
    if string.endswith(ext):
        string = string[:-len(ext)]
    return string

def compress(path):
    with open(path,'r',encoding='utf-8') as f:
        text = f.read()
    counts=Counter(text)
    counts =[(v,k) for k,v in counts.items()]
    htree =hufftree(counts)
    htree.run_huffman_algorithm()
    bits=htree.get_bits()
    table = dict(bits)
    compressed = path + '.huf'
    tr = translate(text,table)
    with open(compressed,'wb') as f:
        pickle.dump((table,tr),f)
    return tr

def decompress(path):
    with open(path,'rb') as ff:
        (table,text)=pickle.load(ff)
    decompressed = remove_extension(path,'.huf')
    dec = translate(text,table,True)
    with open(decompressed,'w',encoding='utf-8') as f:
        print(dec,file=f,end='')
    return dec

def default_compress(path):
    with open('default_table','rb') as ff:
        table=pickle.load(ff)

    with open(path,'r',encoding='utf-8') as f:
        text = f.read()

    compressed = path + '.dhf'
    tr = translate(text,table)

    with open(compressed,'wb') as f:
        pickle.dump(tr,f)

    return tr

def default_decompress(path):
    with open('default_table','rb') as ff:
        table=pickle.load(ff)

    with open(path,'rb') as ff:
        text=pickle.load(ff)

    decompressed = remove_extension(path,'.dhf')
    dec = translate(text,table,True)
    with open(decompressed,'w',encoding='utf-8') as f:
        print(dec,file=f,end='')
    return dec

def translate(string:str,dictionary:dict,reverse=False):
    if reverse==True:
        inv = {v: k for k, v in dictionary.items()}
        str2 = to_bits(string)
        nstr=''
        tmp=''
        for i in str2:
            tmp+=str(i)
            if tmp in inv:
                nstr+=inv[tmp]
                tmp=''
        return nstr

    else:
        tmp = string
        index = 0
        for s in string:
            v = dictionary[s]
            tmp = tmp[:index] + v + tmp[index + 1:]
            index+=len(v)
        fb =from_bits(tmp)
        return fb

def to_bits(text):
    bins = ["{:08b}".format(ord(ch)) for ch in text]
    j = bins[-1]
    bins = bins[:-1]
    f =re.search('10*$',j)
    j=j[:-len(f.group())]
    if len(j)>=1:
        bins = bins + [j]
    return ''.join(bins)


def from_bits(bits):

    ex =(math.ceil(len(bits)/8)*8)-len(bits)
    ex = 8 if ex==0 else ex
    bits = bits +'1'+'0'*(ex-1)
    nums = [bits[i:i+8] for i in range (0,len(bits),8)]
    chars= [chr(int(num, 2)) for num in nums]
    ascii_text = ''.join(chars)
    return ascii_text

def maketable(path):
    with open(path,'r',encoding='utf-8') as f:
        text = f.read()
    counts=Counter(text)
    counts =[(v,k) for k,v in counts.items()]
    htree =hufftree(counts)
    htree.run_huffman_algorithm()
    bits=htree.get_bits()
    table = dict(bits)
    with open('default_table','wb') as f:
        pickle.dump(table,f)

def main():
    n = len(sys.argv)
    if n==2:
        path = path=sys.argv[1]
        if sys.argv[1].endswith('.huf'):
            decompress(path)
        elif sys.argv[1].endswith('.dhf'):
            default_decompress(path)
        else:
            compress(path)
    elif n==3:
        path = sys.argv[2]
        if sys.argv[1]=='--comp' or sys.argv[1]=='-c':
            compress(path)
        elif sys.argv[1]=='--decomp' or sys.argv[1]=='-d':
            decompress(path)
        elif sys.argv[1]=='--default-decompress' or sys.argv[1]=='-dd':
            default_decompress(path)
        elif sys.argv[1]=='--default-compress' or sys.argv[1]=='-dc' or sys.argv[1]=='-cd':
            default_compress(path)
        elif sys.argv[1] == '--maketable' or sys.argv[1] == '-m':
            maketable(path)
        else:
            help()
    else:
        help()

if __name__ == '__main__':
    try:
        main()
    except FileNotFoundError:
        print('\ncannot access the file: No such file or directory')
        help()
    except:
        help()