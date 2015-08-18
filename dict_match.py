# -*- coding: utf-8 -*-
import sys
sys.setrecursionlimit(1000000)
import datetime
import re

class DirtyWordsBase(object):
    """docstring for DirtyWordsBase"""
    def __init__(self, trie):
        self.root = trie.root
        self.special_tag = []

    def init_special_tag(self, special_file=filepath):
        """
        @特殊字符处理，写成与此同时表达式
        """
        import codecs
        result = []
        # 需要转义的字符
        zhuanyi = u'*.?+$^[](){}|\/'
        # 
        if platform.system() == 'Windows':
            special_file = special_file.replace('/', '\\')
        #
        with codecs.open(special_file,'r','utf-8') as fp:
            for eachline in fp:
                word = eachline.strip().strip('\n').strip('\r')
                if word in zhuanyi:
                    if word == '()':
                        word ='\(\)'
                    else:
                        word = '\\' + word
                result.append(word)
        self.special_tag = '|'.join(result)
        # 空格
        self.special_tag += '| '

    def _update(self, src_file, add_file=None):
        """
        update dirty words,delete repetion
        """
        pass

    def _init_trie_tree(self, trie, dirty_words_file):
        """
        @note construct trie tree
        """
        dirty_words_list = self._convert_to_list(dirty_words_file)

        trie = trie._init_from_list(dirty_words_list)
        return trie

    def _check(self,words):
        words = words.lower()
        words = re.sub(self.special_tag, '', words)
        result = self._check_dirty_words(self.root,words)
        return result

    def _check_dirty_words(self, root, words):
        """
        @note检测words文本中是否有脏字，
        如果有返回True,若没有，则返回为False
        将words统一字符转为unicode
        root.is_leaf为判定脏字检测的第一条件
        """
        if root.is_leaf:
            return True
        if not words:
            #判定到字符串的结尾了
            return False
        word = words[0]
        if not root.child.get(word):
            """
            word不在脏字库里面，则跳过word
            以self.root为根结点,检测words[1:]
            """
            if root == self.root:
                words = words[1:]

            root =self.root
            return self._check_dirty_words(root,words)
        else:
            """
            存在以word为头的脏字，更新root,
            """
            root = root.child.get(word)
            words = words[1:]
            return self._check_dirty_words(root, words)

    # 是否检测到最长匹配的脏词或脏句
    def _check_to_leaf(self, node, words, pos):
        while pos < len(words) and node.child.get(words[pos]):
            node = node.child.get(words[pos])
            pos += 1
        # 达到最长路径
        if node.is_leaf:
            return pos
        else:
            return -1

    def _convert_to_list(self,dirty_words_file):
        """
        @读脏字文件，每个脏词一行，逐行读取
        """
        import codecs
        result = []
        with codecs.open(dirty_words_file,'r','utf-8') as fp:
            for eachline in fp:
                result.append(eachline)
        # 去掉读取文件过程中每行结尾处的\r和\n
        result = [i.strip('\n').strip('\r') for i in result]
        return result

    def _convert_to_unicode(self,words):
        """
        @note 统一字符集为unicode,第一个字符占一位
        """
        words = words.decode('utf-8')
        return words

#-------------------Node----------------------------------------------
class Node(object):
    def __init__(self, is_leaf):
        self.child = dict()# 一个个Node节点
        self.is_leaf = is_leaf# 是否

#---------------------------start trie----------------------------------
class Trie(object):
    def __init__(self):
        self.root = Node(False)

    def _add_words(self, words, node):
        '''
        添加一个unicode字符串,亦即插入脏词,每一次的node有变化
        '''
        if len(words) == 0:
            return
        elif len(words) == 1:
            child_node = self.find(node, words[0])
            if child_node:
                child_node.is_leaf = True
                return
            else:
                node.child[words[0]] = Node(True)
                return
        else:
            self._add_words(words[0:1],node)
            node = node.child.get(words[0])
            self._add_words(words[1:], node)

    # 返回word在node中的value
    def find(self, node, word):
        return node.child.get(word)

    def _init_from_list(self, list):
        """
        初始化trie树，并判断各个节点是否为叶子节点
        """
        list = [i.decode('utf-8') if not isinstance(i, unicode) else i for i in list]
        for i in list:
            self._add_words(i, self.root)
        root = self.root
        self._init_leaf(root)

    # 遍历树的每一层，直到结束
    def _print(self, node):
        for k,v in node.child.items():
            print k
            self._print(v)

    # 检测trie树的的叶子节点,将树中所有len(node.child)为0的节点的is_leaf属性置为True
    def _init_leaf(self, node):
        if len(node.child) == 0:
            node.is_leaf = True
        else:
            node.is_leaf = False
            for k,v in node.child.items():
                self._init_leaf(v)