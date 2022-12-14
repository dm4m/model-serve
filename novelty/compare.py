#!/usr/bin/env python3
# coding: utf-8
# File: triple_extraction.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-3-12
import sys

from . import hownet, parser
from .triple_extraction import *
import OpenHowNet
import difflib

class Comparator:
    def __init__(self) -> None:
        pass

    def sovereign_compare(self, extractor, hownet, parser, sovereign_sentence_1, sovereign_triples_1, sovereign_sentence_2, sovereign_triples_2):

        # print(f'\n待比较内容：\n对比专利主权项：{sovereign_sentence_1}\n待申请专利主权项：{sovereign_sentence_2}')
        # print(f'\n待比较内容：\n对比专利主权项：{sovereign_sentence_1}, triple_1：{sovereign_triples_1}\n待申请专利主权项：{sovereign_sentence_2}, triple_2：{sovereign_triples_2}\n审查意见：')
        
        review_flag = 0
        review_opinion = f'\n待比较内容：\n对比专利主权项：{sovereign_sentence_1}, triple_1：{sovereign_triples_1}\n待申请专利主权项："{sovereign_sentence_2}", triple_2：{sovereign_triples_2}\n审查意见：\n'

        # 三元组比较
        for i in range(len(sovereign_triples_1)):
            for j in range(len(sovereign_triples_2)):
                # print(f"sovereign_triples_1[{i}]:",sovereign_triples_1[i])
                # print(f"sovereign_triples_2[{j}]:",sovereign_triples_2[j])
                review_flag, review_opinion = self.direct_substitution(review_flag, review_opinion, hownet, parser, sovereign_triples_1[i], sovereign_triples_2[j])

                review_flag, review_opinion = self.hyponym_hypernym_compare(review_flag, review_opinion, hownet, parser, sovereign_triples_1[i], sovereign_triples_2[j])

                review_flag, review_opinion = self.numeric_range_compare(review_flag, review_opinion, extractor, hownet, parser, sovereign_triples_1[i], sovereign_triples_2[j])

        if review_flag == 0:
            # print('暂未触发相关规则，但存在共有主题词')
            review_opinion += '暂未触发相关规则，但存在共有主题词\n'
        
        return review_opinion

    # 惯用手段的直接置换
    def direct_substitution(self, review_flag, review_opinion, hownet, parser, triple_1, triple_2):

        threshold = 0.4
        if difflib.SequenceMatcher(None, triple_1[1], triple_2[1]).quick_ratio()>=threshold \
                and difflib.SequenceMatcher(None, triple_1[0], triple_2[0]).quick_ratio()>=threshold \
                and difflib.SequenceMatcher(None, triple_1[2], triple_2[2]).quick_ratio()>=threshold \
                and difflib.SequenceMatcher(None, triple_1[0], triple_2[2]).quick_ratio()>=threshold \
                and difflib.SequenceMatcher(None, triple_1[2], triple_2[0]).quick_ratio()>=threshold:
            # print(f"可能涉及惯用手段的直接置换：对比专利三元组{triple_1} 和 待申请专利三元组{triple_2}，可能影响待申请专利的新颖性")
            review_flag += 1
            review_opinion += f"可能涉及惯用手段的直接置换：对比专利三元组{triple_1} 和 待申请专利三元组{triple_2}，可能影响待申请专利的新颖性\n"

        return review_flag, review_opinion

    # 具体(下位) 概念与一般(上位) 概念
    def hyponym_hypernym_compare(self, review_flag, review_opinion, hownet, parser, triple_1, triple_2):
            
        for i in [0,2]:
            words, postags = parser.words_postags(triple_1[i])
            # print("triple_1[i]:", triple_1[i])
            # print("words:", words)
            # print("postags:", postags)
            triple_1[i] = ''
            for j in range(len(words)):
                if postags[j] != 'p' and postags[j] != 'v':
                    triple_1[i] += words[j]
        # print("triple_1:", triple_1)
        for i in [0,2]:
            words, postags = parser.words_postags(triple_2[i])
            triple_2[i] = ''
            for j in range(len(words)):
                if postags[j] != 'p' and postags[j] != 'v':
                    triple_2[i] += words[j]
        # print("triple_1,triple_2:",triple_1,triple_2)

        relation_list = []
        relation_list.append([triple_1[1], triple_2[1], hownet.get_synset_relation(triple_1[1], triple_2[1])]) # 0
        relation_list.append([triple_1[0], triple_2[0], hownet.get_synset_relation(triple_1[0], triple_2[0])]) # 1
        relation_list.append([triple_1[0], triple_2[2], hownet.get_synset_relation(triple_1[0], triple_2[2])]) # 2
        relation_list.append([triple_1[2], triple_2[0], hownet.get_synset_relation(triple_1[2], triple_2[0])]) # 3
        relation_list.append([triple_1[2], triple_2[2], hownet.get_synset_relation(triple_1[2], triple_2[2])]) # 4

        # print("relation_list:", relation_list)
        
        for i in range(1,len(relation_list)):
            if 'hyponym' in relation_list[i][2]:
                # print(f"涉及上下位概念的比较：对比专利三元组{triple_1} 和 待申请专利三元组{triple_2}：{relation_list[i][0]}、{relation_list[i][1]}为上位-下位概念，不影响新颖性")
                review_flag += 1
                review_opinion += f"涉及上下位概念的比较：对比专利三元组{triple_1} 和 待申请专利三元组{triple_2}：{relation_list[i][0]}、{relation_list[i][1]}为上位-下位概念，不影响新颖性\n"
            if 'hypernym' in relation_list[i][2]:
                # print(f"涉及上下位概念的比较：对比专利三元组{triple_1} 和 待申请专利三元组{triple_2}：{relation_list[i][0]}、{relation_list[i][1]}为下位-上位概念，待申请专利的可能不具有新颖性")
                review_flag += 1
                review_opinion += f"涉及上下位概念的比较：对比专利三元组{triple_1} 和 待申请专利三元组{triple_2}：{relation_list[i][0]}、{relation_list[i][1]}为下位-上位概念，待申请专利的可能不具有新颖性\n"
        
        return review_flag, review_opinion
    
    # 数值与数值范围
    def numeric_range_compare(self, review_flag, review_opinion, extractor, hownet, parser, triple_1, triple_2):

        words_triple_1_e2, postags_triple_1_e2 = parser.words_postags(triple_1[2])
        words_triple_2_e2, postags_triple_2_e2 = parser.words_postags(triple_2[2])

        # print(triple_1[0], triple_2[0], difflib.SequenceMatcher(None, triple_1[0], triple_2[0]).quick_ratio())
        # print(triple_1[1], triple_2[1], difflib.SequenceMatcher(None, triple_1[1], triple_2[1]).quick_ratio())
        # print(words_triple_1_e2, postags_triple_1_e2)
        # print(words_triple_2_e2, postags_triple_2_e2)
        if difflib.SequenceMatcher(None, triple_1[0], triple_2[0]).quick_ratio() >= 0.5 and difflib.SequenceMatcher(None, triple_1[1], triple_2[1]).quick_ratio() >= 0.5 and 'm' in postags_triple_1_e2 and 'm' in postags_triple_2_e2: # 若两个三元组的e1、r相似，且e2中均有数词，则进行数值与数值范围比较
            # self.e2_reprocess(parser, triple_1)
            if 'n' not in postags_triple_1_e2 and 'n' not in postags_triple_2_e2:
                number_range_list_without_n_1 = self.e2_number_range_without_n(parser, triple_1[2])
                number_range_list_without_n_2 = self.e2_number_range_without_n(parser, triple_2[2])
                # for i in range(len(number_range_list_without_n_1)):
                #     for j in range(len(number_range_list_without_n_2)):
                #         self.number_range_rules(hownet, number_range_list_without_n_1[i], number_range_list_without_n_2[j])
                review_flag, review_opinion = self.number_range_rules(review_flag, review_opinion, hownet, number_range_list_without_n_1, number_range_list_without_n_2)
            if 'n' in postags_triple_1_e2 and 'n' in postags_triple_2_e2:
                number_range_list_with_n_1 = self.e2_with_n_reprocess(parser, words_triple_1_e2, postags_triple_1_e2)
                number_range_list_with_n_2 = self.e2_with_n_reprocess(parser, words_triple_2_e2, postags_triple_2_e2)
                # print('number_range_list_with_n_1:',number_range_list_with_n_1)
                # print('number_range_list_with_n_2:',number_range_list_with_n_2)
                for i in number_range_list_with_n_1:
                    for j in number_range_list_with_n_2:
                        # print('i:',i,',j:',j,difflib.SequenceMatcher(None, i, j).quick_ratio())
                        if difflib.SequenceMatcher(None, i, j).quick_ratio() >= 0.5 or i in j or j in i:
                            # print(f"涉及数值和数值范围的比较：对比专利{{{i}:{number_range_list_with_n_1[i]}}}，待申请专利{{{j}:{number_range_list_with_n_2[j]}}}")
                            # print('number_range_list_with_n_1[i]:',number_range_list_with_n_1[i])
                            # print('number_range_list_with_n_2[j]:',number_range_list_with_n_2[j])
                            review_flag += 1
                            review_opinion += f"涉及数值和数值范围的比较：对比专利{{{i}:{number_range_list_with_n_1[i]}}}，待申请专利{{{j}:{number_range_list_with_n_2[j]}}}\n"
                            review_flag, review_opinion = self.number_range_rules(review_flag, review_opinion, hownet, number_range_list_with_n_1[i], number_range_list_with_n_2[j])

        return review_flag, review_opinion

    # ['一种铜基形状记忆合金', '包含', '20％锌和5％铝']中的'20％锌和5％铝'再拆分
    def e2_with_n_reprocess(self, parser, words_triple_e2, postags_triple_e2):
        # print(f"words_triple_e2:{words_triple_e2}\npostags_triple_e2:{postags_triple_e2}")

        i = 0
        number_range_list_with_n = {}
        while(i<=len(words_triple_e2)-1):
            if 'm' in postags_triple_e2[i:] and 'n' in postags_triple_e2[i:]:
                m_id = postags_triple_e2.index('m', i)
                n_id = postags_triple_e2.index('n', i)
                if m_id < n_id:
                    # if words_triple_e2[n_id] not in number_range_list_with_n:
                    #     number_range_list_with_n[words_triple_e2[n_id]] = []
                    # number_range_list_with_n[words_triple_e2[n_id]].append(self.e2_number_range_without_n(parser, ''.join(words_triple_e2[m_id:n_id])))
                    number_range_list_with_n[words_triple_e2[n_id]] = self.e2_number_range_without_n(parser, ''.join(words_triple_e2[m_id:n_id]))
                    i = n_id + 1
                if n_id < m_id:
                    cut_end = words_triple_e2.index('n', n_id+1) if 'n' in postags_triple_e2[n_id+1:] else len(words_triple_e2)
                    # if words_triple_e2[n_id] not in number_range_list_with_n:
                    #     number_range_list_with_n[words_triple_e2[n_id]] = []
                    # number_range_list_with_n[words_triple_e2[n_id]].append(self.e2_number_range_without_n(parser, ''.join(words_triple_e2[n_id:cut_end])))
                    number_range_list_with_n[words_triple_e2[n_id]] = self.e2_number_range_without_n(parser, ''.join(words_triple_e2[n_id:cut_end]))
                    i = cut_end
            else:
                break
        return number_range_list_with_n        
    
    # [40, 40, '℃']，[50, 100, '毫米']
    def e2_number_range_without_n(self, parser, sentence):
        words, postags = parser.words_postags(sentence)
        # print(f"words:{words}\npostags:{postags}")
        str_postags = ''.join(postags)
        number_range_list = []

        if 'wp' in postags: # start, end, 单位。词性wp，表示~
            i = 0
            while(i<=len(words)-1):
                if 'wp' in postags[i:]:
                    wp_id = postags.index('wp',i)
                    if wp_id-1 >= 0 and postags[wp_id-1] == 'm': # 70~100毫米，70~100
                        start = float(words[wp_id-1][0:-1])/100 if '%' in words[wp_id-1] or '％' in words[wp_id-1] else float(words[wp_id-1])
                        end = float(words[wp_id+1][0:-1])/100 if '%' in words[wp_id+1] or '％' in words[wp_id-1] else float(words[wp_id+1])
                        unit = '#'
                        i = wp_id + 2
                        if wp_id+2 <= len(words)-1 and postags[wp_id+2] == 'q':
                            unit = words[wp_id+2]
                            i += 1
                        number_range_list.append([start, end, unit])
                        # number_range_list = [start, end, unit]
                    if wp_id-2 >= 0 and postags[wp_id-2] == 'm' and postags[wp_id-1] == 'q': # 40℃~100℃
                        start = float(words[wp_id-2][0:-1])/100 if '%' in words[wp_id-2] or '％' in words[wp_id-1] else float(words[wp_id-2])
                        end = float(words[wp_id+1][0:-1])/100 if '%' in words[wp_id+1] or '％' in words[wp_id-1] else float(words[wp_id+1])
                        unit = words[wp_id-1]
                        number_range_list.append([start, end, unit])
                        # number_range_list = [start, end, unit]
                        i = wp_id + 3
                else:
                    break
        else: # 40     40℃50℃100℃
            i = 0
            while(i<=len(words)-1 and 'q' in postags[i:]): # 有单位
                # if 'q' in postags[i:]: # 词性q，表示单位
                q_id = postags.index('q',i)
                if q_id-1 >= 0 and postags[q_id-1] == 'm':
                    start = float(words[q_id-1][0:-1])/100 if '%' in words[q_id-1] or '％' in words[q_id-1] else float(words[q_id-1])
                    end = float(words[q_id-1][0:-1])/100 if '%' in words[q_id-1] or '％' in words[q_id-1] else float(words[q_id-1])
                    unit = words[q_id]
                    number_range_list.append([start, end, unit])
                    # number_range_list = [start, end, unit]
                    i = q_id + 1
                # else:
                #     break
            i = 0 
            while(i<=len(words)-1 and 'q' not in postags[i:]): # 无单位 40
                j = 0
                while(j<=len(words[i])-1):
                    if '%' in words[i]:
                        percent_id = words[i].index('%',j)
                        start = float(words[i][j:percent_id])/100
                        end = start
                        unit = '#'
                        number_range_list.append([start, end, unit])
                        # number_range_list = [start, end, unit]
                        j = percent_id + 1
                    elif '％' in words[i]:
                        percent_id = words[i].index('％',j)
                        start = float(words[i][j:percent_id])/100
                        end = start
                        unit = '#'
                        number_range_list.append([start, end, unit])
                        # number_range_list = [start, end, unit]
                        j = percent_id + 1
                    else:
                        start = float(words[i])
                        end = float(words[i])
                        unit = '#'
                        number_range_list.append([start, end, unit])
                        # number_range_list = [start, end, unit]
                        break
                i += 1

        # print("number_range_list:",number_range_list)
        return number_range_list
        
    def number_range_rules(self, review_flag, review_opinion, hownet, number_range_list_1, number_range_list_2):

        for i in range(len(number_range_list_1)):
            for j in range(len(number_range_list_2)):

                # if hownet.calculate_word_similarity(number_range_1[2],number_range_2[2]) == 1: # 若两组单位相同，才进行比较
                if number_range_list_1[i][2] == number_range_list_2[j][2]: # 若两组单位相同，才进行比较

                    # 1
                    if (number_range_list_2[j][0] < number_range_list_2[j][1]) and (number_range_list_2[j][0] <= number_range_list_1[i][0] == number_range_list_1[i][1] <= number_range_list_2[j][1]):
                        print(f"(1)对比专利公开的数值{number_range_list_1[i][0]} 落在 待申请专利的数值范围{number_range_list_2[j]}内，将破坏 要求保护的发明或者实用新型的新颖性")
                        review_flag += 1
                        review_opinion += f"(1)对比专利公开的数值{number_range_list_1[i][0]} 落在 待申请专利的数值范围{number_range_list_2[j]}内，将破坏 要求保护的发明或者实用新型的新颖性\n"
                    if (number_range_list_2[j][0] < number_range_list_2[j][1]) and (number_range_list_2[j][0] <= number_range_list_1[i][0] < number_range_list_1[i][1] <= number_range_list_2[j][1]):
                        print(f"(1)对比专利公开的数值范围{number_range_list_1[i]} 落在 待申请专利的数值范围{number_range_list_2[j]}内，将破坏 要求保护的发明或者实用新型的新颖性")
                        review_flag += 1
                        review_opinion += f"(1)对比专利公开的数值范围{number_range_list_1[i]} 落在 待申请专利的数值范围{number_range_list_2[j]}内，将破坏 要求保护的发明或者实用新型的新颖性\n"

                    # 2
                    # print(f"({number_range_list_1[i][0]} < {number_range_list_1[i][1]}) and ({number_range_list_2[j][0]} < {number_range_list_2[j][1]}) and (({number_range_list_2[j][0]} <= {number_range_list_1[i][0]} <= {number_range_list_2[j][1]}) or ({number_range_list_2[j][0]} <= {number_range_list_1[i][1]} <= {number_range_list_2[j][1]}))")
                    if (number_range_list_1[i][0] < number_range_list_1[i][1]) and (number_range_list_2[j][0] < number_range_list_2[j][1]) and ((number_range_list_2[j][0] <= number_range_list_1[i][0] <= number_range_list_2[j][1]) or (number_range_list_2[j][0] <= number_range_list_1[i][1] <= number_range_list_2[j][1])):
                        print(f"(2)对比专利公开的数值范围{number_range_list_1[i]} 和 待申请专利的数值范围{number_range_list_2[j]}部分重叠或者有一个共同的端点，将破坏 要求保护的发明或者实用新型的新颖性")
                        review_flag += 1
                        review_opinion += f"(2)对比专利公开的数值范围{number_range_list_1[i]} 和 待申请专利的数值范围{number_range_list_2[j]}部分重叠或者有一个共同的端点，将破坏 要求保护的发明或者实用新型的新颖性\n"

                    # 3
                    if (number_range_list_1[i][0] < number_range_list_1[i][1]) and (number_range_list_2[j][0] == number_range_list_2[j][1]):
                        if number_range_list_2[j][0] == number_range_list_1[i][0] or number_range_list_2[j][0] == number_range_list_1[i][1]:
                            # print(f"(3)对比专利公开的数值范围{number_range_list_1[i]}的两个端点 将破坏 待申请专利的技术特征{number_range_list_2[j][0]}为离散数值并且具有该两端点中任一个的发明或者实用新型的新颖性")
                            review_flag += 1
                            review_opinion += f"(3)对比专利公开的数值范围{number_range_list_1[i]}的两个端点 将破坏 待申请专利的技术特征{number_range_list_2[j][0]}为离散数值并且具有该两端点中任一个的发明或者实用新型的新颖性\n"
                        if number_range_list_1[i][0] < number_range_list_2[j][0] < number_range_list_1[i][1]:
                            # print(f"(3)对比专利公开的数值范围{number_range_list_1[i]}的两个端点 不破坏 待申请专利的技术特征{number_range_list_2[j][0]}为该两端点之间任一数值的发明或者实用新型的新颖性")
                            review_flag += 1
                            review_opinion += f"(3)对比专利公开的数值范围{number_range_list_1[i]}的两个端点 不破坏 待申请专利的技术特征{number_range_list_2[j][0]}为该两端点之间任一数值的发明或者实用新型的新颖性\n"

                    # 4
                    if number_range_list_1[i][0] < number_range_list_2[j][0] < number_range_list_2[j][1] < number_range_list_1[i][1]:
                        # print(f"(4)待申请专利的技术特征的数值或者数值范围{number_range_list_2[j]}落在对比文件公开的数值范围{number_range_list_1[i]}内，并且与对比文件公开的数值范围没有共同的端点，则对比文件 不破坏 要求保护的发明或者实用新型的新颖性")
                        review_flag += 1
                        review_opinion += f"(4)待申请专利的技术特征的数值或者数值范围{number_range_list_2[j]}落在对比文件公开的数值范围{number_range_list_1[i]}内，并且与对比文件公开的数值范围没有共同的端点，则对比文件 不破坏 要求保护的发明或者实用新型的新颖性\n"
        
        return review_flag, review_opinion

def novelty_compare(main_sig, com_sig):
    patent_1_sentences_list, patent_1_sovs_list, extractor = triple_extraction_main(com_sig)
    patent_2_sentences_list, patent_2_sovs_list, extractor = triple_extraction_main(main_sig)
    comparator = Comparator()
    print('\n**********************比较开始**********************\n')
    # 输出
    review_opinion = comparator.sovereign_compare(extractor, hownet, parser, patent_1_sentences_list,
                                                  patent_1_sovs_list, patent_2_sentences_list, patent_2_sovs_list)
    print(review_opinion)
    return review_opinion

'''测试'''
def compare_main():
    # OpenHowNet.download()
    hownet = OpenHowNet.HowNetDict(init_sim=True, init_babel=True)
    parser = LtpParser()
    
    # 输入
    sovereign_content_1 = '5.一种铜基形状记忆合金，包含20％(重量) 锌和5％(重量) 铝。'
    sovereign_content_2 = '5.一种铜基形状记忆合金，包含10％～35％(重量) 的锌和2％～8％(重量) 的铝，余量为铜。'

    patent_1_sentences_list, patent_1_sovs_list, extractor= triple_extraction_main(sovereign_content_1)
    patent_2_sentences_list, patent_2_sovs_list, extractor = triple_extraction_main(sovereign_content_2)

    comparator = Comparator()

    

    print('\n\n\n\n\n\n**********************比较开始**********************\n')

    # 输出
    review_opinion = comparator.sovereign_compare(extractor, hownet, parser, patent_1_sentences_list, patent_1_sovs_list, patent_2_sentences_list, patent_2_sovs_list)
    
    f = open('data/output.txt', "w", encoding='utf-8')
    f.write(review_opinion)
    f.close()

    # hownet = OpenHowNet.HowNetDict(init_sim=True, init_babel=True)
    # print(hownet.calculate_word_similarity('卤素','氟'))
    # print(hownet.get_synset_relation('卤素','氟'))
    # print(hownet.calculate_word_similarity('铜','金属'))
    # print(hownet.get_synset_relation('金属','铜'))
    # print(hownet.get_synset_relation('铜','金属'))
    # print(difflib.SequenceMatcher(None, '某产品','某产品').quick_ratio())
    # print(difflib.SequenceMatcher(None, '卤素','氟').quick_ratio())
    # print(difflib.SequenceMatcher(None, '铜','金属').quick_ratio())
    # print(difflib.SequenceMatcher(None, '构成','组成').quick_ratio())
    # print(difflib.SequenceMatcher(None, '选用','采用').quick_ratio())
    # print(difflib.SequenceMatcher(None, '为','用').quick_ratio())
    # print(hownet.calculate_word_similarity('构成','组成'))
    # print(hownet.calculate_word_similarity('选用','采用'))
    # print(hownet.get_synset_relation('构成','组成'))
    # print(hownet.get_synset_relation('螺钉','螺栓'))
    # print(hownet.calculate_word_similarity('螺钉','螺栓'))

    # word_1 = [3,5,7,3,5,7]
    # print(word_1.find(1))
    # print(word_1.index(3,2))
    # words_2 = word_1.copy()
    # words_2.append(5)
    # print(word_1)
    # print(words_2)
    # del words_2[2:3]
    # print(words_2)

    # if 1 < 2==2 <=3:
    #     print("yes")
    # word_1 = ['3','5','7','3','5','7']
    # print(word_1[2:4])
    # print(str(word_1[2:4]))
    # word_2 = ''.join(word_1[2:4])
    # print(word_2)

def test_novelty_compare():
    print(sys.path)
    sovereign_content_1 = '5.一种铜基形状记忆合金，包含20％(重量) 锌和5％(重量) 铝。'
    sovereign_content_2 = '5.一种铜基形状记忆合金，包含10％～35％(重量) 的锌和2％～8％(重量) 的铝，余量为铜。'
    print(novelty_compare(sovereign_content_2, sovereign_content_1))


# compare_main()
# test_novelty_compare()