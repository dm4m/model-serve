import os
import re

from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller


class LtpParser:
    def __init__(self):
        LTP_DIR = os.path.dirname(__file__) + "/ltp_data_v3.4.0"
        user_dict = os.path.dirname(__file__) + '/data/dict.txt'

        # # pyltp 0.2.1
        # self.segmentor = Segmentor()
        # self.segmentor.load_with_lexicon(os.path.join(LTP_DIR, "cws.model"), user_dict)

        # self.postagger = Postagger()
        # self.postagger.load_with_lexicon(os.path.join(LTP_DIR, "pos.model"), user_dict)

        # self.parser = Parser()
        # self.parser.load(os.path.join(LTP_DIR, "parser.model"))

        # self.recognizer = NamedEntityRecognizer()
        # self.recognizer.load(os.path.join(LTP_DIR, "ner.model"))

        # self.labeller = SementicRoleLabeller()
        # self.labeller.load(os.path.join(LTP_DIR, 'pisrl.model'))

        # pyltp 0.4.0
        self.segmentor = Segmentor(os.path.join(LTP_DIR, "cws.model"), user_dict)
        self.postagger = Postagger(os.path.join(LTP_DIR, "pos.model"))
        self.parser = Parser(os.path.join(LTP_DIR, "parser.model"))
        self.recognizer = NamedEntityRecognizer(os.path.join(LTP_DIR, "ner.model"))
        self.labeller = SementicRoleLabeller(os.path.join(LTP_DIR, 'pisrl.model'))

    '''语义角色标注'''
    def format_labelrole(self, words, postags, arcs):
        roles = self.labeller.label(words, postags, arcs)
        # print("len(roles) = {0}----roles = {1}".format(len(roles), roles))
        roles_dict = {}
        for index,arguments in roles:
            # print("谓语所在索引：role.index = {0}".format(role.index))
            # for arg in arguments:
            #     print(index,arg[0],arg[1][0],arg[1][1]) 
            # role[0]:role.index
            # arg[0]:arg.name
            # arg[1][0]:arg.range.start
            # arg[1][1]:arg.range.end
            roles_dict[index] = {arg[0]:[arg[0],arg[1][0], arg[1][1]] for arg in arguments}
        # print("语义角色标注---->roles_dict = {0}".format(roles_dict))
        return roles_dict

    '''句法分析---为句子中的每个词语维护一个保存句法依存儿子节点的字典'''
    def build_parse_child_dict(self, words, postags, arcs): # words：分词后的结果；postags：词性标注后的结果；arcs：依存句法分析树
        # print("-" * 50, "依存句法分析：开始", "-" * 50)
        child_dict_list = []
        format_parse_list = []
        # print("分词列表：words = {}".format(words))
        # print("词性分析：postags = {}".format(postags))
        # for arc in arcs:
            # print(arc[0],arc[1])
            # print(arc.head,arc.relation)
        rely_ids = [arc[0] - 1 for arc in arcs]  # 提取该句话的每一个词的依存父节点id【0为ROOT，词语从1开始编号】: [2, 0, 2, 5, 8, 8, 6, 3] - 1 =  [1, -1, 1, 4, 7, 7, 5, 2]【此时 -1 表示ROOT】
        # print("各个词语所依赖的父节点：rely_ids = {0}".format(rely_ids))
        heads = ['Root' if rely_id == -1 else words[rely_id] for rely_id in rely_ids]  # 匹配依存父节点词语
        # print("各个词语所依赖的父节点词语 = {0}".format(heads))
        relations = [arc[1] for arc in arcs]  # 提取依存关系
        # print("各个词语与所依赖的父节点的依赖关系 = {0}".format(relations))

        for word_index in range(len(words)):
            # print("\nword_index = {0}----word = {1}".format(word_index, words[word_index]))
            child_dict = dict() # 每个词语与所有其他词语的关系字典
            for arc_index in range(len(arcs)):  # arc_index==0时表示ROOT【还没进入“我想听一首迪哥的歌”语句】，arc_index==1时表示“我”
                # 当“依存句法分析树”遍历，遇到当前词语时，说明当前词语在依存句法分析树中与其他词语有依存关系
                if word_index == rely_ids[arc_index]:  # arcs[arc_index].head 表示arcs[arc_index]所代表的词语依存弧的父结点的索引。 ROOT 节点的索引是 0 ，第一个词开始的索引依次为1，2，3，···【“我”的索引为1】arc. relation 表示依存弧的关系。
                    # print("word_index = {0}----arc_index = {1}----rely_ids[arc_index] = {2}----relations[arc_index] = {3}".format(word_index, arc_index, rely_ids[arc_index], relations[arc_index]))
                    if relations[arc_index] in child_dict:  # arcs[arc_index].relation表示arcs[arc_index]所代表的词语与父节点的依存关系(语法关系)
                        child_dict[relations[arc_index]].append(arc_index) # 添加 child_dict = {'ATT': [4]}----> child_dict = {'ATT': [4, 5]}
                    else:
                        child_dict[relations[arc_index]] = [] # 新建
                        child_dict[relations[arc_index]].append(arc_index)  # child_dict = {[]}----> child_dict = {'ATT': [4]}
                    # print("child_dict = {0}".format(child_dict))
            child_dict_list.append(child_dict)# 每个词对应的依存关系父节点和其关系
            # print("child_dict_list = {0}".format(child_dict_list))
        # 整合每个词语的句法依存关系
        for i in range(len(words)):
            # a = [relations[i], words[i], i, postags[i], heads[i], rely_ids[i]-1, postags[rely_ids[i]-1]]
            a = [relations[i], words[i], i, postags[i], heads[i], rely_ids[i], postags[rely_ids[i]]]
            format_parse_list.append(a)
        # print("整合每个词语的句法依存关系---->format_parse_list = ", format_parse_list)
        # print("-" * 50, "依存句法分析：结束", "-" * 50)
        return child_dict_list, format_parse_list

    # 4 μ m : m q ws
    # -10.0 % : m wp
    def correct_mqws(self, words, postags):
        words_1 = []
        postags_1 = []
        i = 0
        while(i <= len(words)-2):
            if postags[i]=='m' and postags[i+1]=='q':
                words_1.append(words[i]+words[i+1])
                postags_1.append('m')
                i += 2
            else:
                words_1.append(words[i])
                postags_1.append(postags[i])
                i += 1
        words_1 += words[i:]
        postags_1 += postags[i:]

        words_2 = []
        postags_2 = []
        i = 0
        while(i <= len(words_1)-2):
            if postags_1[i]=='m' and postags_1[i+1]=='ws':
                words_2.append(words_1[i]+words_1[i+1])
                postags_2.append('m')
                i += 2
            else:
                words_2.append(words_1[i])
                postags_2.append(postags_1[i])
                i += 1
        words_2 += words_1[i:]
        postags_2 += postags_1[i:]

        # print('2:',words_2,postags_2)

        # -10.0 % : m wp
        words_3 = []
        postags_3 = []
        i = 0
        # while(i<=len(words_2)-2):
        for i in range(len(words_2)):
            if postags_2[i] == 'm' and '-' in words_2[i] and words_2[i].index('-') == 0:
                words_3.append('-')
                postags_3.append('wp')
                words_3.append(words_1[i].replace('-',''))
                postags_3.append('m')
            else:
                words_3.append(words_2[i])
                postags_3.append(postags_2[i])
        # print('3:',words_3,postags_3)
        words_4 = []
        postags_4 = []
        i = 0
        while(i<=len(words_3)-2):
            if postags_3[i] == 'm' and words_3[i+1] in ['%', '％']:
                words_4.append(words_3[i]+words_3[i+1])
                postags_4.append('m')
                i += 2
            else:
                words_4.append(words_3[i])
                postags_4.append(postags_3[i])
                i += 1
        words_4 += words_3[i:]
        postags_4 += postags_3[i:]
        # print('4:',words_4,postags_4)
        return words_4, postags_4

    def correct_postags(self, words, postags):
        for i in range(len(words)-1):
            if words[i] == '所述' and postags[i+1] == 'v':
                postags[i+1] = 'n'
        return postags

    def one_number(self, number, unit):
        word = []
        postag = []
        if len(unit) == 0:
            word.append(number)
            postag.append('m')
        else:
            if '%' in unit:
                word.append(number + '%')
                postag.append('m')
                word.append(unit[1:]) if unit[1:] != '' else None
                postag.append('q') if unit[1:] != '' else None
            else:
                word.append(number)
                word.append(unit)
                postag.append('m')
                postag.append('q')
        return word, postag

    def number_range_words_postags(self, HanLP, sentence):

        number_list = re.findall(r'\d+', sentence)
        unit_list = re.findall(r'\D+', sentence)
        words = []
        postags = []
        if len(number_list) == 1:
            words, postags = self.one_number(number_list[0], unit_list[0]) if unit_list!=[] else self.one_number(number_list[0], [])

        if '-' in sentence and len(number_list) == 2:
            split_sentence = sentence.split('-')

            number_1 = re.findall(r'\d+', split_sentence[0])
            unit_1 = re.findall(r'\D+', split_sentence[0])
            words_temp_1, postags_temp_1 = self.one_number(number_1[0], unit_1[0]) if unit_1!=[] else self.one_number(number_1[0], [])
            words += words_temp_1
            postags += postags_temp_1

            words += '-'
            postags += 'w'

            number_2 = re.findall(r'\d+', split_sentence[1])
            unit_2 = re.findall(r'\D+', split_sentence[1])
            words_temp_2, postags_temp_2 = self.one_number(number_2[0], unit_2[0]) if unit_2!=[] else self.one_number(number_2[0], [])
            words += words_temp_2
            postags += postags_temp_2

        if len(number_list) > 2:
            words, postags = self.words_postags(HanLP, sentence)

        return words, postags


    # 三元组的e2进行处理
    def words_postags(self, HanLP, sentence): #此处先用hanlp分，如果分不开(分词数为1)再用ltp分

        # words = list(self.segmentor.segment(sentence))
        # postags = list(self.postagger.postag(words))
        # print("words,postags:",words,postags)

        doc = HanLP(sentence, tasks=['tok/fine','pos/pku'])
        words = doc['tok/fine']
        postags = doc['pos/pku']
        # print("words,postags:",words,postags)

        words_1 = []
        postags_1 = []
        i = 0
        while(i<=len(words)-2):
            if words[i] == 'μ' and words[i+1] == 'm':
                words_1.append('μm')
                postags_1.append('q')
                i += 2
            else:
                words_1.append(words[i])
                postags_1.append(postags[i])
                i += 1
        words_1 = words_1 + words[i:] if i<=len(words)-1 else words_1
        postags_1 = postags_1 + postags[i:] if i<=len(words)-1 else postags_1
        # print("words_1,postags_1:",words_1,postags_1)

        words_2 = []
        postags_2 = []
        for i in range(len(words_1)):
            if postags_1[i] != 'c': # 删掉连词
                words_2.append(words_1[i])
                postags_2.append(postags_1[i])
        # print("words_2,postags_2:",words_2,postags_2)

        # # -10.0 % : m wp
        # words_3 = []
        # postags_3 = []
        # i = 0
        # # while(i<=len(words_2)-2):
        # for i in range(len(words_2)):
        #     if postags_2[i] == 'm' and '-' in words_2[i]:
        #         words_3.append('-')
        #         postags_3.append('wp')
        #         words_3.append(words_2[i].replace('-',''))
        #         postags_3.append('m')
        #     else:
        #         words_3.append(words_2[i])
        #         postags_3.append(postags_2[i])
        # # print("words_3,postags_3:",words_3,postags_3)

        words_3 = words_2
        postags_3 = postags_2
        words_4 = []
        postags_4 = []
        i = 0
        while(i<=len(words_3)-2):
            if postags_3[i] == 'm' and words_3[i+1] in ['%', '％']:
                words_4.append(words_3[i]+words_3[i+1])
                postags_4.append('m')
                i += 2
            else:
                words_4.append(words_3[i])
                postags_4.append(postags_3[i])
                i += 1
        words_4 = words_4 + words_3[i:] if i<=len(words_3)-1 else words_4
        postags_4 = postags_4 + postags_3[i:] if i<=len(words_3)-1 else postags_4
        # print("words_4,postags_4:",words_4,postags_4)

        return words_4, postags_4

    

    '''parser主函数'''
    def parser_main(self, HanLP, sentence):

        table = {ord(f): ord(t) for f, t in zip(
            u'：～~，．。！？【】（）％＃＠＆１２３４５６７８９０ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ',
            u':--,..!?[]()%#@&1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')}
        sentence = sentence.translate(table)

        doc = HanLP(sentence, tasks=['tok/fine','pos/pku', 'ner/msra'])
        words = doc['tok/fine']
        postags = doc['pos/pku']

        # words = list(self.segmentor.segment(sentence))
        # postags = list(self.postagger.postag(words))

        words, postags = self.correct_mqws(words, postags)
        postags = self.correct_postags(words, postags)
        arcs = self.parser.parse(words, postags) # 建立依存句法分析树
        
        child_dict_list, format_parse_list = self.build_parse_child_dict(words, postags, arcs)
        roles_dict = self.format_labelrole(words, postags, arcs)

        return words, postags, child_dict_list, roles_dict, format_parse_list, doc

