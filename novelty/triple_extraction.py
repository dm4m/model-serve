from .sentence_parser import *
import re

class TripleExtractor:
    def __init__(self):
        self.parser = LtpParser()

    '''文章分句处理, 切分长句，冒号，分号，感叹号等做切分标识'''
    def split_sents(self, content):
        return [sentence for sentence in re.split(r'[？?！!。；;：:\n\r]', content) if sentence]

    '''利用语义角色标注,直接获取主谓宾三元组,基于A0,A1,A2'''
    def ruler1(self, words, postags, roles_dict, role_index):
        v = words[role_index]
        role_info = roles_dict[role_index]
        if 'A0' in role_info.keys() and 'A1' in role_info.keys():
            # s = ''.join([words[word_index] for word_index in range(role_info['A0'][1], role_info['A0'][2]+1) if
            #              postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]])
            # o = ''.join([words[word_index] for word_index in range(role_info['A1'][1], role_info['A1'][2]+1) if
            #              postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]])
            s = ''.join([words[word_index] for word_index in range(role_info['A0'][1], role_info['A0'][2]+1) if
                         (postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]) or (postags[word_index][0] == 'w' and words[word_index] in ['~', '～', '-'])])
            o = ''.join([words[word_index] for word_index in range(role_info['A1'][1], role_info['A1'][2]+1) if
                         (postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]) or (postags[word_index][0] == 'w' and words[word_index] in ['~', '～', '-'])])
            if s and o:
                return '1', [s, v, o]
        if 'A0' in role_info.keys() and 'A2' in role_info.keys():
            # s = ''.join([words[word_index] for word_index in range(role_info['A0'][1], role_info['A0'][2]+1) if
            #              postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]])
            # o = ''.join([words[word_index] for word_index in range(role_info['A2'][1], role_info['A2'][2]+1) if
            #              postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]])
            s = ''.join([words[word_index] for word_index in range(role_info['A0'][1], role_info['A0'][2]+1) if
                         (postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]) or (postags[word_index][0] == 'w' and words[word_index] in ['~', '～', '-'])])
            o = ''.join([words[word_index] for word_index in range(role_info['A2'][1], role_info['A2'][2]+1) if
                         (postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]) or (postags[word_index][0] == 'w' and words[word_index] in ['~', '～', '-'])])
            if s and o:
                return '1', [s, v, o]
        if 'A1' in role_info.keys() and 'MNR' in role_info.keys():
            # s = ''.join([words[word_index] for word_index in range(role_info['MNR'][1], role_info['MNR'][2]+1) if
            #              postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]])
            # o = ''.join([words[word_index] for word_index in range(role_info['A1'][1], role_info['A1'][2]+1) if
            #              postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]])
            s = ''.join([words[word_index] for word_index in range(role_info['MNR'][1], role_info['MNR'][2]+1) if
                         (postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]) or (postags[word_index][0] == 'w' and words[word_index] in ['~', '～', '-'])])
            o = ''.join([words[word_index] for word_index in range(role_info['A1'][1], role_info['A1'][2]+1) if
                         (postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]) or (postags[word_index][0] == 'w' and words[word_index] in ['~', '～', '-'])])
            if s and o:
                return '1', [s, v, o]
        # elif 'A0' in role_info:
        #     s = ''.join([words[word_index] for word_index in range(role_info['A0'][1], role_info['A0'][2] + 1) if
        #                  postags[word_index][0] not in ['w', 'u', 'x']])
        #     if s:
        #         return '2', [s, v]
        # elif 'A1' in role_info:
        #     o = ''.join([words[word_index] for word_index in range(role_info['A1'][1], role_info['A1'][2]+1) if
        #                  postags[word_index][0] not in ['w', 'u', 'x']])
        #     return '3', [v, o]
        return '4', []

    '''三元组抽取主函数'''
    def ruler2(self, words, postags, child_dict_list, arcs, roles_dict, doc):
        svos = []
        for index in range(len(postags)):
            tmp = 1
            # 先借助语义角色标注的结果，进行三元组抽取
            if index in roles_dict:
                flag, triple = self.ruler1(words, postags, roles_dict, index)
                if flag == '1':
                    triple = self.svo_process(triple, words, postags)
                    # triple[0] = self.complete_e(words, postags, child_dict_list, child_dict['SBV'][0], arcs)
                    # triple[2] = self.complete_e(words, postags, child_dict_list, child_dict['VOB'][0], arcs)
                    triple[2] = self.complete_m(words, postags, words.index(triple[2]), arcs) if triple[2] in words else triple[2]
                    # if words.index(triple[2]):
                    #     triple[2] = self.complete_m(self, words, postags, words.index(triple[2]), arcs)
                    svos.append(triple)
                    # print("三元组--语义角色标注:", triple)
                    tmp = 0
            if tmp == 1:
                # 如果语义角色标记为空，则使用依存句法进行抽取
                # if postags[index] == 'v':
                if postags[index]:
                # 抽取以谓词为中心的事实三元组
                    child_dict = child_dict_list[index]
                    # 主谓宾
                    if 'SBV' in child_dict and 'VOB' in child_dict: # SBV 主谓关系，VOB 动宾关系
                        r = words[index]
                        e1 = self.complete_e(words, postags, child_dict_list, child_dict['SBV'][0], arcs)
                        e2 = self.complete_e(words, postags, child_dict_list, child_dict['VOB'][0], arcs)
                        # triple = [e1, r, e2]
                        triple = self.svo_process([e1, r, e2], words, postags)
                        if triple != [] and triple not in svos:
                            svos.append(triple)
                            # print("三元组--以谓词为中心:",triple)


                    '''if 'SBV' in child_dict and 'v' not in postags and 'WP' in child_dict:
                        print('here!')
                        r = ''
                        e1 = self.complete_e(words, postags, child_dict_list, child_dict['SBV'][0], arcs)
                        e2 = self.complete_e(words, postags, child_dict_list, child_dict['WP'][0], arcs)
                        print(f'e1:{e1},r:{r},e2:{e2}')
                        triple = self.svo_process([e1, r, e2], words, postags)
                        if triple != [] and triple not in svos:
                            svos.append(triple)'''

                    # 定语后置，动宾关系
                    relation = arcs[index][0]
                    head = arcs[index][2]
                    if relation == 'ATT':
                        if 'VOB' in child_dict:
                            e1 = self.complete_e(words, postags, child_dict_list, head-1, arcs)
                            r = words[index]
                            e2 = self.complete_e(words, postags, child_dict_list, child_dict['VOB'][0], arcs)
                            temp_string = r + e2
                            if temp_string == e1[:len(temp_string)]:
                                e1 = e1[len(temp_string):]
                            if temp_string not in e1:
                                triple = self.svo_process([e1, r, e2], words, postags)
                                if triple != [] and triple not in svos:
                                    svos.append(triple)
                                    # print("三元组--定语后置，动宾关系:",triple)
                    # 含有介宾关系的主谓动补关系
                    if 'SBV' in child_dict and 'CMP' in child_dict: # CMP动补
                        e1 = self.complete_e(words, postags, child_dict_list, child_dict['SBV'][0], arcs)
                        cmp_index = child_dict['CMP'][0]
                        r = words[index] + words[cmp_index]
                        if 'POB' in child_dict_list[cmp_index]:
                            e2 = self.complete_e(words, postags, child_dict_list, child_dict_list[cmp_index]['POB'][0], arcs)
                            triple = self.svo_process([e1, r, e2], words, postags)
                            if triple != [] and triple not in svos:
                                svos.append(triple)
                                # print("三元组--含有介宾关系的主谓动补关系:",triple)

                    if postags[index] == 'v' and 'SBV' in child_dict:
                        e1 = self.complete_e(words, postags, child_dict_list, child_dict['SBV'][0], arcs)
                        r = words[index]
                        if 'ADV' in child_dict:
                            for i in range(len(child_dict['ADV'])):
                                if postags[child_dict['ADV'][i]] == 'p':
                                    adv_index = child_dict['ADV'][i]
                                    if words[adv_index+1] and postags[adv_index+1] == 'n':
                                        r = words[adv_index] + words[adv_index+1] + r
                                    if 'POB' in child_dict_list[adv_index]:
                                        e2 = self.complete_e(words, postags, child_dict_list, child_dict_list[adv_index]['POB'][0], arcs)
                                        triple = self.svo_process([e1, r, e2], words, postags)
                                        if triple != [] and triple not in svos:
                                            svos.append(triple)
                                            # print("三元组--动词在最后:",triple)

        for ner in doc['ner/msra']:
            idx = doc['tok/fine'].index(ner[0])
            if idx != -1:
                if idx - 1 >= 0 and doc['pos/pku'][idx - 1] == 'n' and doc['tok/fine'][idx - 1] not in ['权利要求']:
                    svos.append([doc['tok/fine'][idx-1],'为', ner[0]])
                elif idx + 1 < len(doc['tok/fine']) and doc['pos/pku'][idx + 1] == 'n' and doc['tok/fine'][idx + 1] not in ['权利要求']:
                    svos.append([doc['tok/fine'][idx + 1], '为', ner[0]])

        return svos

    # 对找出的主语或者宾语进行扩展
    # 主语不考虑连词、左附加LAD关系和右附加RAD关系
    def complete_e(self, words, postags, child_dict_list, word_index, arcs):
        child_dict = child_dict_list[word_index]
        prefix = ''
        if 'ATT' in child_dict: # ATT 定中关系    红苹果（红<--苹果）
            for i in range(len(child_dict['ATT'])):
                prefix += self.complete_e(words, postags, child_dict_list, child_dict['ATT'][i], arcs)
        postfix = ''
        if postags[word_index] == 'v':
            if 'VOB' in child_dict:
                postfix += self.complete_e(words, postags, child_dict_list, child_dict['VOB'][0], arcs)
            if 'SBV' in child_dict:
                prefix = self.complete_e(words, postags, child_dict_list, child_dict['SBV'][0], arcs) + prefix

        # if type == 'subject':
        #     return prefix + words[word_index] + postfix
        # else: # 宾语 数词       LAD/RAD+连词
        # rely_word = arcs[word_index][4]
        # rely_id = arcs[word_index][5]
        # rely_postag = arcs[word_index][6]
        # for i in range(len(words)-1, -1):
        #     if i == rely_id:
        # if postags[word_index] == 'm' and rely_id and rely_postag == 'm' and rely_id <= word_index:
        #     postfix = words.slice(rely_id, word_index) + postfix
        return prefix + words[word_index] + postfix

    def complete_m(self, words, postags, word_index, arcs):
        rely_word = arcs[word_index][4]
        rely_id = arcs[word_index][5]
        rely_postag = arcs[word_index][6]
        if postags[word_index] == 'm' and rely_id and rely_postag == 'm' and rely_id <= word_index:
            prefix = ''.join(words[rely_id:word_index])
        else:
            prefix = ''
        return prefix + words[word_index]


    def svo_process(self, triple, words, postags):
        triple[0] = triple[0].replace('所述', '')
        triple[1] = triple[1].replace('所述', '')
        triple[2] = triple[2].replace('所述', '')
        if '其特征' in triple[0] and '权利要求' in triple[1]:
            triple = []
            return triple

        for i in range(3):
            if triple[i] in words and postags[words.index(triple[i])]=='u': # u 助词
                triple = []
                return triple

        if triple[0] != '' and triple[1] != '' and triple[2] != '':
            return triple
        else:
            triple = []
            return triple

    '''程序主控函数'''
    def sovereigns_triples(self, HanLP, content):
        sentences = self.split_sents(content)
        svos = []
        for sentence in sentences:
            words, postags, child_dict_list, roles_dict, arcs, doc = self.parser.parser_main(HanLP, sentence)
            # relation={arcs[24][0]}, word={arcs[24][1]}, id={arcs[24][2]}, postag={arcs[24][3]}
            # rely_word={arcs[24][4]}, rely_id={arcs[24][5]}, rely_postag={arcs[24][6]}
            svo = self.ruler2(words, postags, child_dict_list, arcs, roles_dict, doc)
            svos += svo
        return svos

def content_process(content):
    content = re.sub(u"\\(.*?\\)", "", content) # 去除(21)等括号及括号内的内容
    content = re.sub(u" ", "", content) # 去除空格
    flag = content.index('.')
    content = content[flag+1:]
    return content


'''测试'''
def triple_extraction_main(HanLP, sovereign_content):
    
    extractor = TripleExtractor()

    sentences_list = []
    svos_list = []
    content = re.sub(u" ", "", sovereign_content) # 去除空格
    sentences_list.append(content)

    content = content_process(content)
    svos_list = extractor.sovereigns_triples(HanLP, content)

    return sentences_list, svos_list, extractor

