#!/usr/bin/env python3
# coding: utf-8
# File: triple_extraction.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-3-12
import sys

from . import *
from .triple_extraction import *
import OpenHowNet
import difflib
import os

import multiprocessing
import time

class Comparator:
    def __init__(self) -> None:
        pass

    def sovereign_compare(self, extractor, sovereign_sentence_1, sovereign_triples_1, sovereign_sentence_2, sovereign_triples_2):

        # print(f'\n待比较内容：\n对比专利主权项：{sovereign_sentence_1}\n待申请专利主权项：{sovereign_sentence_2}\n审查意见：')
        print(f'\n待比较内容：\n对比专利主权项：{sovereign_sentence_1}, triple_1：{sovereign_triples_1}\n待申请专利主权项：{sovereign_sentence_2}, triple_2：{sovereign_triples_2}\n审查意见：')

        x = time.time()
        sovereign_triples_1_substitution_words, triples_copy_1 = self.substitution_words_for_direct_substitution(sovereign_triples_1)
        sovereign_triples_2_substitution_words, triples_copy_2 = self.substitution_words_for_direct_substitution(sovereign_triples_2)
        y = time.time()
        print("获得置换词时间：", y - x)

        review_flag = 0
        review_opinion = ''
        # review_opinion = f'\n待比较内容：\n对比专利主权项：{sovereign_sentence_1}\n待申请专利主权项："{sovereign_sentence_2}"\n审查意见：\n'
        # review_opinion = f'\n待比较内容：\n对比专利主权项：{sovereign_sentence_1}, triple_1：{sovereign_triples_1}\n待申请专利主权项："{sovereign_sentence_2}", triple_2：{sovereign_triples_2}\n审查意见：\n'

        # 词比较
        # a = time.time()
        review_flag, review_opinion, words_info = self.wordlevel_point(review_flag, review_opinion, sovereign_sentence_1, sovereign_sentence_2)
        # b = time.time()
        # print("词比较时间：", b-a)

        # 三元组比较
        for i in range(len(sovereign_triples_1)):
            for j in range(len(sovereign_triples_2)):
                # print(f"\n本轮三元组：{sovereign_triples_1[i], sovereign_triples_2[j]}")
                # a = time.time()
                review_flag, review_opinion = self.direct_substitution(review_flag, review_opinion, sovereign_triples_1[i], sovereign_triples_2[j], triples_copy_1[i], triples_copy_2[j], sovereign_triples_1_substitution_words[i], sovereign_triples_2_substitution_words[j])
                # b = time.time()
                # print("惯用手段的直接置换时间：", b-a)
                review_flag, review_opinion = self.hyponym_hypernym_compare(review_flag, review_opinion, sovereign_triples_1[i], sovereign_triples_2[j])
                # c = time.time()
                # print("上下位比较时间：", c-b)
                review_flag, review_opinion = self.numeric_range_compare(review_flag, review_opinion, extractor, sovereign_triples_1[i], sovereign_triples_2[j])
                # d = time.time()
                # print("数值范围比较时间：", d - c)
                # print(f"本轮总时间：{d-a}")

        if review_flag == 0:
            print('暂未触发相关规则。')
            review_opinion += '暂未触发相关规则。\n'
        
        return review_opinion, words_info

    def relations_translation(self, relations):
        relations_chinese = []
        for i in relations:
            relations_chinese.append(relations_map[i]) if relations_map[i] not in relations_chinese else None
        return relations_chinese


    # 两句主权项对比word-level高亮显示
    def wordlevel_point(self, review_flag, review_opinion, sovereign_sentence_1, sovereign_sentence_2):
        # a = time.time()

        sdp_feature_1, srl_feature_1, ner_feature_1 = highlight(sovereign_sentence_1)
        # sdp_feature_2, srl_feature_2, ner_feature_2 = highlight(sovereign_sentence_2)

        info_1 = []
        for word in sdp_feature_1:
            if word[0] not in info_1 and len(word[0]) <= 10:
                info_1.append(word[0])
        for word in ner_feature_1:
            if word[0] not in info_1 and len(word[0]) <= 10:
                info_1.append(word[0])
        for word in srl_feature_1:
            if word not in info_1 and len(word) <= 10:
                info_1.append(word)

        # info_2 = []
        # for word in sdp_feature_2:
        #     if word[0] not in info_2 and len(word[0]) <= 10:
        #         info_2.append(word[0])
        # for word in ner_feature_2:
        #     if word[0] not in info_2 and len(word[0]) <= 10:
        #         info_2.append(word[0])
        # for word in srl_feature_2:
        #     if word not in info_2 and len(word) <= 10:
        #         info_2.append(word)

        doc_2 = HanLP(sovereign_sentence_2, tasks=['tok/fine','pos/pku'])
        words_2 = doc_2['tok/fine']
        pos_2 = doc_2['pos/pku']

        word_pairs = []
        info_set = []
        for word_1 in info_1:
            for idx, word_2 in enumerate(words_2):
                relation = hownet.get_synset_relation(word_1, word_2)
                if pos_2[idx] == 'n' and [word_1, word_2] not in word_pairs and relation != []:
                    word_pairs.append([word_1, word_2])
                    info_set.append([word_1, word_2, self.relations_translation(relation)])

        info_set_copy = info_set.copy()
        for idx, info in enumerate(info_set_copy):
            start_1 = sovereign_sentence_1.find(info[0])
            start_2 = sovereign_sentence_2.find(info[1])
            if start_1 != -1 and start_2 != -1:
                end_1 = start_1 + len(info[0])
                end_2 = start_2 + len(info[1])
                info_set[idx].insert(1, [start_1, end_1])
                info_set[idx].insert(3, [start_2, end_2])
            else:
                info_set.remove(info)

        print("info_set:", info_set)
        # b = time.time()
        # print("wordlevel_point耗时：",b-a)


        # # 词之间的关系比较
        # HanLP['tok/fine'].config.output_spans = True
        # doc_1 = HanLP(sovereign_sentence_1, tasks=['tok/fine','pos/pku','sdp','ner'])
        # doc_2 = HanLP(sovereign_sentence_2, tasks=['tok/fine','pos/pku','sdp','ner'])
        # words_realtion = []
        # words_info = []
        # for index1,word1 in enumerate(doc_1['tok/fine']):
        #     for index2,word2 in enumerate(doc_2['tok/fine']):
        #         if doc_1['pos/pku'][index1]=='n' and doc_2['pos/pku'][index2]=='n' and word1[0]!=word2[0] and word1[0]!='特征' and word2[0]!='特征':
        #             relation = hownet.get_synset_relation(word1[0],word2[0])
        #             if relation!=[] and [word1[0],word2[0],relation] not in words_realtion:
        #                 words_realtion.append([word1[0],word2[0],relation])
        #                 # print(f"{word1[0]} {word2[0]} {relation}")
        #                 # print(f"{word1[0]} {word2[0]} {self.relations_translation(relation)}")
        #                 words_info.append([word1, word2, self.relations_translation(relation)])
        #                 print(f"{word1} {word2} {self.relations_translation(relation)}")
        #                 review_flag += 1
        #                 review_opinion += f"{word1[0]} {word2[0]} {self.relations_translation(relation)}\n"
        # HanLP['tok/fine'].config.output_spans = False
        #
        # print("words_info:", words_info)
        # b = time.time()
        # print("wordlevel_point耗时：",b-a)
        return review_flag, review_opinion, info_set

    # 得到惯用手段的直接置换的substitution_words
    def substitution_words_for_direct_substitution(self, sovereign_triples):
        sovereign_triples_substitution_words = []
        triples_copy = sovereign_triples.copy()
        for idx, triple in enumerate(sovereign_triples):

            for i in [0, 2]:
                words, postags = parser.words_postags(HanLP, triple[i])
                triples_copy[idx][i] = ''
                for j in range(len(words)):
                    if postags[j] != 'p':  # 删除介词
                        triples_copy[idx][i] += words[j]

            sovereign_triples_substitution_words.append(self.substitution_words(bu, triples_copy[idx], 1))
        return sovereign_triples_substitution_words, triples_copy

    def substitution_words(self, bu, triple, flag):
        substitution_words = []
        related_e1 = bu.get_related(triple[0])
        related_e2 = bu.get_related(triple[2])
        another_name_e1 = bu.another_name(triple[0])
        another_name_e2 = bu.another_name(triple[2])

        substitution_words += related_e1['has_part'] if 'has_part' in related_e1 else []
        substitution_words += related_e1['subclass_of'] if 'subclass_of' in related_e1 else []
        substitution_words += related_e2['has_part'] if 'has_part' in related_e2 else []
        substitution_words += related_e2['subclass_of'] if 'subclass_of' in related_e2 else []
        if flag == 1:
            substitution_words += another_name_e1 if another_name_e1 != [] else []
            substitution_words += another_name_e2 if another_name_e2 != [] else []

        return substitution_words
    # 惯用手段的直接置换
    def direct_substitution(self, review_flag, review_opinion, triple_1, triple_2, triple_copy_1, triple_copy_2, substitution_words_1, substitution_words_2):

        # triple_copy_1 = triple_1.copy()
        # triple_copy_2 = triple_2.copy()
        #
        # for i in [0, 2]:
        #     words, postags = parser.words_postags(HanLP, triple_copy_1[i])
        #     triple_copy_1[i] = ''
        #     for j in range(len(words)):
        #         if postags[j] != 'p': # 删除介词
        #             triple_copy_1[i] += words[j]
        # for i in [0, 2]:
        #     words, postags = parser.words_postags(HanLP, triple_copy_2[i])
        #     triple_copy_2[i] = ''
        #     for j in range(len(words)):
        #         if postags[j] != 'p':  # 删除介词
        #             triple_copy_2[i] += words[j]
        # # print(triple_copy_1, triple_copy_2)
        # substitution_words_1 = self.substitution_words(bu, triple_copy_1, 1)
        # substitution_words_2 = self.substitution_words(bu, triple_copy_2, 1)
        # # print(substitution_words_1, substitution_words_2)

        # substitution_words_1 = sovereign_triples_1_substitution_words[triple_copy_1]
        # substitution_words_2 = sovereign_triples_2_substitution_words[triple_copy_2]

        # threshold = 0.4
        # if difflib.SequenceMatcher(None, triple_1[1], triple_2[1]).quick_ratio()>=threshold and difflib.SequenceMatcher(None, triple_1[0], triple_2[0]).quick_ratio()>=threshold and difflib.SequenceMatcher(None, triple_1[2], triple_2[2]).quick_ratio()>=threshold and difflib.SequenceMatcher(None, triple_1[0], triple_2[2]).quick_ratio()>=threshold and difflib.SequenceMatcher(None, triple_1[2], triple_2[0]).quick_ratio()>=threshold:
        if triple_copy_1[0] in substitution_words_2 or triple_copy_1[2] in substitution_words_2 or triple_copy_2[0] in substitution_words_1 or triple_copy_2[2] in substitution_words_1:
            print(f"可能涉及惯用手段的直接置换：对比专利三元组{triple_1} 和 待申请专利三元组{triple_2}，可能影响待申请专利的新颖性")
            review_flag += 1
            review_opinion += f"\n可能涉及惯用手段的直接置换：对比专利三元组{triple_1} 和 待申请专利三元组{triple_2}，可能影响待申请专利的新颖性\n"

        return review_flag, review_opinion

    # 具体(下位) 概念与一般(上位) 概念
    def hyponym_hypernym_compare(self, review_flag, review_opinion, triple_1, triple_2):

        triple_copy_1 = triple_1.copy()
        triple_copy_2 = triple_2.copy()
            
        for i in [0,2]:
            words, postags = parser.words_postags(HanLP, triple_copy_1[i])
            triple_copy_1[i] = ''
            for j in range(len(words)):
                if postags[j] != 'p' and postags[j] != 'v':
                    triple_copy_1[i] += words[j]
        # print("triple_1:", triple_1)
        for i in [0,2]:
            words, postags = parser.words_postags(HanLP, triple_copy_2[i])
            triple_copy_2[i] = ''
            for j in range(len(words)):
                if postags[j] != 'p' and postags[j] != 'v':
                    triple_copy_2[i] += words[j]
        # print("triple_1,triple_2:",triple_1,triple_2)

        relation_list = []
        relation_list.append([triple_copy_1[1], triple_copy_2[1], hownet.get_synset_relation(triple_copy_1[1], triple_copy_2[1])]) # 0
        relation_list.append([triple_copy_1[0], triple_copy_2[0], hownet.get_synset_relation(triple_copy_1[0], triple_copy_2[0])]) # 1
        relation_list.append([triple_copy_1[0], triple_copy_2[2], hownet.get_synset_relation(triple_copy_1[0], triple_copy_2[2])]) # 2
        relation_list.append([triple_copy_1[2], triple_copy_2[0], hownet.get_synset_relation(triple_copy_1[2], triple_copy_2[0])]) # 3
        relation_list.append([triple_copy_1[2], triple_copy_2[2], hownet.get_synset_relation(triple_copy_1[2], triple_copy_2[2])]) # 4

        # print("relation_list:", relation_list)

        review_flag_temp = review_flag
        for i in range(1,len(relation_list)):
            if 'hyponym' in relation_list[i][2]:
                print(f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{relation_list[i][0]}、{relation_list[i][1]}为上位-下位概念，不影响新颖性")
                review_flag += 1
                review_opinion += f"\n涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{relation_list[i][0]}、{relation_list[i][1]}为上位-下位概念，不影响新颖性\n"
            if 'hypernym' in relation_list[i][2]:
                print(f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{relation_list[i][0]}、{relation_list[i][1]}为下位-上位概念，待申请专利的可能不具有新颖性")
                review_flag += 1
                review_opinion += f"\n涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{relation_list[i][0]}、{relation_list[i][1]}为下位-上位概念，待申请专利的可能不具有新颖性\n"

        # if review_flag == review_flag_temp:
        #     # t1_e1_hypernym = bu.hypernym(triple_copy_1[0]) # 上位词
        #     # t1_e2_hypernym = bu.hypernym(triple_copy_1[2])
        #     # t1_e1_hyponymy = bu.hyponymy(triple_copy_1[0]) # 下位词
        #     # t1_e2_hyponymy = bu.hyponymy(triple_copy_1[2])
        #     t2_e1_hypernym = bu.hypernym(triple_copy_2[0]) # 上位词
        #     t2_e2_hypernym = bu.hypernym(triple_copy_2[2])
        #     t2_e1_hyponymy = bu.hyponymy(triple_copy_2[0]) # 下位词
        #     t2_e2_hyponymy = bu.hyponymy(triple_copy_2[2])
        #
        #     if triple_copy_1[0] != triple_copy_2[0]:
        #         # if triple_copy_1[0] in t2_e1_hypernym or triple_copy_2[0] in t1_e1_hyponymy: # 上位-下位
        #         if triple_copy_1[0] in t2_e1_hypernym:  # 上位-下位
        #             print(f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{triple_copy_1[0]}、{triple_copy_2[0]}为上位-下位概念，不影响新颖性")
        #             review_flag += 1
        #             review_opinion += f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{triple_copy_1[0]}、{triple_copy_2[0]}为上位-下位概念，不影响新颖性\n"
        #         # if triple_copy_1[0] in t2_e1_hyponymy or triple_copy_2[0] in t1_e1_hypernym: # 下位-上位
        #         if triple_copy_1[0] in t2_e1_hyponymy:  # 下位-上位
        #             print(f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{triple_copy_1[0]}、{triple_copy_2[0]}为下位-上位概念，不影响新颖性")
        #             review_flag += 1
        #             review_opinion += f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{triple_copy_1[0]}、{triple_copy_2[0]}为下位-上位概念，不影响新颖性\n"
        #
        #     if triple_copy_1[0] != triple_copy_2[2]:
        #         # if triple_copy_1[0] in t2_e2_hypernym or triple_copy_2[2] in t1_e1_hyponymy: # 上-下
        #         if triple_copy_1[0] in t2_e2_hypernym:  # 上-下
        #             print(f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{triple_copy_1[0]}、{triple_copy_2[2]}为上位-下位概念，不影响新颖性")
        #             review_flag += 1
        #             review_opinion += f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{triple_copy_1[0]}、{triple_copy_2[2]}为上位-下位概念，不影响新颖性\n"
        #         # if triple_copy_1[0] in t2_e2_hyponymy or triple_copy_2[2] in t1_e1_hypernym: # 下-上
        #         if triple_copy_1[0] in t2_e2_hyponymy:  # 下-上
        #             print(f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{triple_copy_1[0]}、{triple_copy_2[2]}为下位-上位概念，不影响新颖性")
        #             review_flag += 1
        #             review_opinion += f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{triple_copy_1[0]}、{triple_copy_2[2]}为下位-上位概念，不影响新颖性\n"
        #
        #     if triple_copy_1[2] != triple_copy_2[0]:
        #         # if triple_copy_1[2] in t2_e1_hypernym or triple_copy_2[0] in t1_e2_hyponymy: # 上-下
        #         if triple_copy_1[2] in t2_e1_hypernym:  # 上-下
        #             print(f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{triple_copy_1[2]}、{triple_copy_2[0]}为上位-下位概念，不影响新颖性")
        #             review_flag += 1
        #             review_opinion += f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{triple_copy_1[2]}、{triple_copy_2[0]}为上位-下位概念，不影响新颖性\n"
        #         # if triple_copy_1[2] in t2_e1_hyponymy or triple_copy_2[0] in t1_e2_hypernym: # 下-上
        #         if triple_copy_1[2] in t2_e1_hyponymy:  # 下-上
        #             print(f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{triple_copy_1[2]}、{triple_copy_2[0]}为下位-上位概念，不影响新颖性")
        #             review_flag += 1
        #             review_opinion += f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{triple_copy_1[2]}、{triple_copy_2[0]}为下位-上位概念，不影响新颖性\n"
        #
        #     if triple_copy_1[2] != triple_copy_2[2]:
        #         # if triple_copy_1[2] in t2_e2_hypernym or triple_copy_2[2] in t1_e2_hyponymy: # 上-下
        #         if triple_copy_1[2] in t2_e2_hypernym:  # 上-下
        #             print(f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{triple_copy_1[2]}、{triple_copy_2[2]}为上位-下位概念，不影响新颖性")
        #             review_flag += 1
        #             review_opinion += f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{triple_copy_1[2]}、{triple_copy_2[2]}为上位-下位概念，不影响新颖性\n"
        #         # if triple_copy_1[2] in t2_e2_hyponymy or triple_copy_2[2] in t1_e2_hypernym: # 下-上
        #         if triple_copy_1[2] in t2_e2_hyponymy:  # 下-上
        #             print(f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{triple_copy_1[2]}、{triple_copy_2[2]}为下位-上位概念，不影响新颖性")
        #             review_flag += 1
        #             review_opinion += f"涉及上下位概念的比较：对比专利三元组{triple_copy_1} 和 待申请专利三元组{triple_copy_2}：{triple_copy_1[2]}、{triple_copy_2[2]}为下位-上位概念，不影响新颖性\n"

        return review_flag, review_opinion
    
    # 数值与数值范围
    def numeric_range_compare(self, review_flag, review_opinion, extractor, triple_1, triple_2):

        words_triple_1_e2, postags_triple_1_e2 = parser.words_postags(HanLP, triple_1[2])
        words_triple_2_e2, postags_triple_2_e2 = parser.words_postags(HanLP, triple_2[2])


        if difflib.SequenceMatcher(None, triple_1[0], triple_2[0]).quick_ratio() >= 0.5 and difflib.SequenceMatcher(None, triple_1[1], triple_2[1]).quick_ratio() >= 0.5 and self.is_digital(words_triple_1_e2, postags_triple_1_e2) and self.is_digital(words_triple_2_e2, postags_triple_2_e2) and words_triple_1_e2.count('-')<2 and words_triple_2_e2.count('-')<2: # 若两个三元组的e1、r相似，且e2中均有数词，则进行数值与数值范围比较

            if 'n' not in postags_triple_1_e2 and 'n' not in postags_triple_2_e2:
                number_range_list_without_n_1 = self.e2_number_range_without_n(parser, HanLP, triple_1[2])
                number_range_list_without_n_2 = self.e2_number_range_without_n(parser, HanLP, triple_2[2])
                tmp_review_opinion = review_opinion
                tmp_review_flag = review_flag
                tmp_review_flag, tmp_review_opinion = self.number_range_rules(tmp_review_flag, tmp_review_opinion, hownet, number_range_list_without_n_1, number_range_list_without_n_2)
                if tmp_review_flag > review_flag:
                    review_flag = tmp_review_flag
                    review_opinion = review_opinion + f"\n涉及数值和数值范围的比较：对比专利{triple_1}，待申请专利{triple_2}\n" + tmp_review_opinion.replace(review_opinion, '')
            if 'n' in postags_triple_1_e2 and 'n' in postags_triple_2_e2:
                number_range_list_with_n_1 = self.e2_with_n_reprocess(parser, HanLP, words_triple_1_e2, postags_triple_1_e2)
                number_range_list_with_n_2 = self.e2_with_n_reprocess(parser, HanLP, words_triple_2_e2, postags_triple_2_e2)
                for i in number_range_list_with_n_1:
                    for j in number_range_list_with_n_2:
                        if difflib.SequenceMatcher(None, i, j).quick_ratio() >= 0.5 or i in j or j in i:
                            print(f"涉及数值和数值范围的比较：对比专利{{{i}:{number_range_list_with_n_1[i]}}}，待申请专利{{{j}:{number_range_list_with_n_2[j]}}}")
                            review_flag += 1
                            review_opinion += f"\n涉及数值和数值范围的比较：对比专利{{{i}:{number_range_list_with_n_1[i]}}}，待申请专利{{{j}:{number_range_list_with_n_2[j]}}}\n"
                            review_flag, review_opinion = self.number_range_rules(review_flag, review_opinion, hownet, number_range_list_with_n_1[i], number_range_list_with_n_2[j])

        return review_flag, review_opinion

    def is_digital(self, words, postags):
        for idx, postag in enumerate(postags):
            if postag == 'm' and re.findall(r'\d+', words[idx]) != []:
                return True
        return False

    # ['一种铜基形状记忆合金', '包含', '20％锌和5％铝']中的'20％锌和5％铝'再拆分
    def e2_with_n_reprocess(self, parser, HanLP, words_triple_e2, postags_triple_e2):
        # print(f"words_triple_e2:{words_triple_e2}\npostags_triple_e2:{postags_triple_e2}")

        i = 0
        number_range_list_with_n = {}
        while(i<=len(words_triple_e2)-1):
            # if 'm' in postags_triple_e2[i:] and 'n' in postags_triple_e2[i:]:
            if self.is_digital(words_triple_e2[i:], postags_triple_e2[i:]) and 'n' in postags_triple_e2[i:]:
                m_id = postags_triple_e2.index('m', i)
                n_id = postags_triple_e2.index('n', i)
                if m_id < n_id:
                    # if words_triple_e2[n_id] not in number_range_list_with_n:
                    #     number_range_list_with_n[words_triple_e2[n_id]] = []
                    # number_range_list_with_n[words_triple_e2[n_id]].append(self.e2_number_range_without_n(parser, ''.join(words_triple_e2[m_id:n_id])))
                    number_range_list_with_n[words_triple_e2[n_id]] = self.e2_number_range_without_n(parser, HanLP, ''.join(words_triple_e2[m_id:n_id]))
                    i = n_id + 1
                if n_id < m_id:
                    cut_end = words_triple_e2.index('n', n_id+1) if 'n' in postags_triple_e2[n_id+1:] else len(words_triple_e2)
                    # if words_triple_e2[n_id] not in number_range_list_with_n:
                    #     number_range_list_with_n[words_triple_e2[n_id]] = []
                    # number_range_list_with_n[words_triple_e2[n_id]].append(self.e2_number_range_without_n(parser, ''.join(words_triple_e2[n_id:cut_end])))
                    number_range_list_with_n[words_triple_e2[n_id]] = self.e2_number_range_without_n(parser, HanLP, ''.join(words_triple_e2[n_id:cut_end]))
                    i = cut_end
            else:
                break
        return number_range_list_with_n        
    
    # [40, 40, '℃']，[50, 100, '毫米']
    def e2_number_range_without_n(self, parser, HanLP, sentence):
        words, postags = parser.number_range_words_postags(HanLP, sentence)
        # print(f"words:{words}\npostags:{postags}")
        # str_postags = ''.join(postags)
        number_range_list = []

        if 'w' in postags: # start, end, 单位。词性wp，表示~
            i = 0
            while(i<=len(words)-1):
                if 'w' in postags[i:]:
                    wp_id = postags.index('w',i)
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
                    isdigit_flag = 0
                    if ('%' in words[q_id - 1] or '％' in words[q_id - 1]) and words[q_id-1][0:-1].isdigit():
                        start = float(words[q_id-1][0:-1])/100
                        end = start
                        isdigit_flag += 1
                    if '%' not in words[q_id - 1] and '％' not in words[q_id - 1] and words[q_id-1].isdigit():
                        start = float(words[q_id-1])
                        end = start
                        isdigit_flag += 1
                    # start = float(words[q_id-1][0:-1])/100 if ('%' in words[q_id-1] or '％' in words[q_id-1]) else float(words[q_id-1])
                    # end = float(words[q_id-1][0:-1])/100 if ('%' in words[q_id-1] or '％' in words[q_id-1]) else float(words[q_id-1])
                    if isdigit_flag > 0:
                        unit = words[q_id]
                        number_range_list.append([start, end, unit])
                        # number_range_list = [start, end, unit]
                        i = q_id + 1
                # else:
                #     break
            i = 0 
            while(i<=len(words)-1 and 'q' not in postags[i:] and 'm' in postags[i:]): # 无单位 40
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

    # 4条数值与数值范围比较规则 
    def number_range_rules(self, review_flag, review_opinion, hownet, number_range_list_1, number_range_list_2):

        for i in range(len(number_range_list_1)):
            for j in range(len(number_range_list_2)):

                # if hownet.calculate_word_similarity(number_range_1[2],number_range_2[2]) == 1: # 若两组单位相同，才进行比较
                # if number_range_list_1[i][2] == number_range_list_2[j][2]: # 若两组单位相同，才进行比较
                if 1==1:

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
                            print(f"(3)对比专利公开的数值范围{number_range_list_1[i]}的两个端点 将破坏 待申请专利的技术特征{number_range_list_2[j][0]}为离散数值并且具有该两端点中任一个的发明或者实用新型的新颖性")
                            review_flag += 1
                            review_opinion += f"(3)对比专利公开的数值范围{number_range_list_1[i]}的两个端点 将破坏 待申请专利的技术特征{number_range_list_2[j][0]}为离散数值并且具有该两端点中任一个的发明或者实用新型的新颖性\n"
                        if number_range_list_1[i][0] < number_range_list_2[j][0] < number_range_list_1[i][1]:
                            print(f"(3)对比专利公开的数值范围{number_range_list_1[i]}的两个端点 不破坏 待申请专利的技术特征{number_range_list_2[j][0]}为该两端点之间任一数值的发明或者实用新型的新颖性")
                            review_flag += 1
                            review_opinion += f"(3)对比专利公开的数值范围{number_range_list_1[i]}的两个端点 不破坏 待申请专利的技术特征{number_range_list_2[j][0]}为该两端点之间任一数值的发明或者实用新型的新颖性\n"

                    # 4
                    if number_range_list_1[i][0] < number_range_list_2[j][0] < number_range_list_2[j][1] < number_range_list_1[i][1]:
                        print(f"(4)待申请专利的技术特征的数值或者数值范围{number_range_list_2[j]}落在对比文件公开的数值范围{number_range_list_1[i]}内，并且与对比文件公开的数值范围没有共同的端点，则对比文件 不破坏 要求保护的发明或者实用新型的新颖性")
                        review_flag += 1
                        review_opinion += f"(4)待申请专利的技术特征的数值或者数值范围{number_range_list_2[j]}落在对比文件公开的数值范围{number_range_list_1[i]}内，并且与对比文件公开的数值范围没有共同的端点，则对比文件 不破坏 要求保护的发明或者实用新型的新颖性\n"

                    # 5
                    if (number_range_list_1[i][0] == number_range_list_2[j][0]) and (number_range_list_1[i][1] == number_range_list_2[j][1]):
                        print(f"(5)待申请专利的技术特征的数值或者数值范围{number_range_list_2[j]}与对比文件公开的数值范围{number_range_list_1[i]}相同，则对比文件 将破坏 要求保护的发明或者实用新型的新颖性")
                        review_flag += 1
                        review_opinion += f"(5)待申请专利的技术特征的数值或者数值范围{number_range_list_2[j]}与对比文件公开的数值范围{number_range_list_1[i]}相同，则对比文件 将破坏 要求保护的发明或者实用新型的新颖性\n"

                    # 6
                    if (number_range_list_1[i][0] <= number_range_list_1[i][1]) and (number_range_list_2[j][0] <= number_range_list_2[j][1]) and ((number_range_list_1[i][0] > number_range_list_2[j][1]) or (number_range_list_1[i][1] < number_range_list_2[j][0])):
                        print(f"(6)待申请专利的技术特征的数值或者数值范围{number_range_list_2}与对比文件公开的数值范围{number_range_list_1}不重合，对比文件 不破坏 要求保护的发明或者实用新型的新颖性")
                        review_flag += 1
                        review_opinion += f"(6)待申请专利的技术特征的数值或者数值范围{number_range_list_2}与对比文件公开的数值范围{number_range_list_1}不重合，对比文件 不破坏 要求保护的发明或者实用新型的新颖性\n"
        
        return review_flag, review_opinion

def  highlight(sentence):
    sdp_feature = []
    srl_feature = []
    ner_feature = []

    doc = HanLP(sentence, tasks=['tok/fine', 'pos/pku', 'sdp', 'srl', 'ner'])

    # sdp 语义依存分析
    # sdp_feature = []
    for idx, relations in enumerate(doc['sdp']):
        for relation in relations:
            sdp_feature.append([doc['tok/fine'][idx], relation[1]]) if relation[1] == 'Tool' or relation[1] == 'Matl' else None

    # srl 语义角色标注
    # srl_feature = []
    for idx, tuples in enumerate(doc['srl']):
        if idx==0 and len(doc['srl'])>1:
            continue
        else:
            for tuple in tuples: # tuple样式：[["添加剂", "ARG0", 17, 18], ["为", "PRED", 18, 19], ["N-甲基-4-硝基苯胺、三-（2-氯乙基）磷酸酯、邻苯二酚中任意一种", "ARG1", 19, 41]]
                if tuple[1] == 'ARG0' or tuple[1] == 'ARG1':
                    flag = 0
                    for tmp in sdp_feature:
                        if tuple[0].find(tmp[0])!=-1:
                            flag += 1
                            break
                    if flag == 0:
                        srl_feature.append(tuple[0])

    # 长度、时间、百分比等信息及其主体高亮显示
    # ner_feature = []
    for ner in doc['ner/msra']:
        idx = doc['tok/fine'].index(ner[0])
        if idx!=-1:
            if idx-1>=0 and doc['pos/pku'][idx-1]=='n' and doc['tok/fine'][idx-1] not in ['权利要求']:
                ner_feature.append([doc['tok/fine'][idx-1], ner])
            elif idx+1<len(doc['tok/fine']) and doc['pos/pku'][idx+1]=='n' and doc['tok/fine'][idx+1] not in ['权利要求']:
                ner_feature.append([doc['tok/fine'][idx+1], ner])

    print(f"主权项：{sentence}")
    print("sdp_feature:", sdp_feature) if sdp_feature!=[] else None # [['铜', 'Matl']]
    print("srl_feature:", srl_feature) if srl_feature!=[] else None # ['添加剂', 'N-甲基-4-硝基苯胺、三-（2-氯乙基）磷酸酯、邻苯二酚中任意一种']
    print('ner_feature:', ner_feature) if ner_feature!=[] else None # [['铜', ('30', 'WEIGHT', 3, 4)], ['铝', ('60g', 'LENGTH', 7, 8)]]
    # review = f"主权项：{sentence}\n"
    # review = review + f"{sdp_feature}\n" if sdp_feature != [] else None
    # review = review + f"{srl_feature}\n" if srl_feature != [] else None
    # review = review + str(f"{ner_feature}\n") if ner_feature != [] else None
    return sdp_feature, srl_feature, ner_feature

# sdp_feature, srl_feature, ner_feature是直接从原句中得出的重点词
# sdp_related_info, srl_related_info, ner_related_info是与重点词相关的词
def search_related(sentence):
    sdp_feature = []
    srl_feature = []
    ner_feature = []

    sdp_feature, srl_feature, ner_feature = highlight(sentence)
    sdp_related_info = {}
    srl_related_info = {}
    ner_related_info = {}
    for i in sdp_feature:
        if len(i[0]) <= 10:
            related_info = bu.get_related(i[0])
            if related_info != {}:
                sdp_related_info[i[0]] = related_info
    for i in srl_feature:
        if len(i) <= 10:
            related_info = bu.get_related(i)
            if related_info != {}:
                srl_related_info[i] = related_info
    for i in ner_feature:
        if len(i[0]) <= 10:
            related_info = bu.get_related(i[0])
            if related_info != {}:
                ner_related_info[i[0]] = related_info

    print("sdp_related_info:", sdp_related_info) if sdp_related_info != {} else None
    print("srl_related_info:", srl_related_info) if srl_related_info != {} else None
    print("ner_related_info:", ner_related_info) if ner_related_info != {} else None

    return sdp_feature, srl_feature, ner_feature, sdp_related_info, srl_related_info, ner_related_info

def get_related_words(related_info, word_2, info_set, word_pairs):
    for word_1 in related_info:
        for relation in related_info[word_1]:
            if word_2 in related_info[word_1][relation]:
                if [word_1, word_2] not in word_pairs:
                    word_pairs.append([word_1, word_2])
                    info_set.append([word_1, word_2, [relation]])
                else:
                    idx = word_pairs.index([word_1, word_2])
                    if relation not in info_set[idx][2]:
                        info_set[idx][2].append(relation)
    return info_set, word_pairs
def words_compare(sentence_1, sentence_2):
    a = time.time()
    info_set = []
    word_pairs = []
    sdp_feature, srl_feature, ner_feature, sdp_related_info, srl_related_info, ner_related_info = search_related(sentence_1)
    words_2 = HanLP(sentence_2, tasks='tok/fine')['tok/fine']
    for word_2 in words_2:
        info_set, word_pairs = get_related_words(sdp_related_info, word_2, info_set, word_pairs)
        info_set, word_pairs = get_related_words(srl_related_info, word_2, info_set, word_pairs)
        info_set, word_pairs = get_related_words(ner_related_info, word_2, info_set, word_pairs)

    info_set_copy = info_set.copy()
    for idx, info in enumerate(info_set_copy):
        start_1 = sentence_1.find(info[0])
        start_2 = sentence_2.find(info[1])
        if start_1 != -1 and start_2 != -1:
            end_1 = start_1 + len(info[0])
            end_2 = start_2 + len(info[1])
            info_set[idx].insert(1, [start_1, end_1])
            info_set[idx].insert(3, [start_2, end_2])
        else:
            info_set.remove(info)
    b = time.time()
    print("words_compare耗时:", b-a)
    return info_set

def novelty_compare(main_sig, com_sig):

    # doc = HanLP("根据权利要求1-4任一项所述的炸药，其特征在于，所述纳米玄武岩粉的粒径为10-100nm。", tasks=['tok/fine', 'pos/pku', 'sdp', 'srl', 'ner'])
    # print(doc)

    # review_opinion = ''
    a = time.time()
    patent_1_sentences_list, patent_1_sovs_list, extractor = triple_extraction_main(HanLP, main_sig)
    patent_2_sentences_list, patent_2_sovs_list, extractor = triple_extraction_main(HanLP, com_sig)
    b = time.time()
    print("抽取三元组时间：", b-a)
    comparator = Comparator()
    # 输出
    c = time.time()
    review_opinion, words_info = comparator.sovereign_compare(extractor, patent_1_sentences_list[0], patent_1_sovs_list, patent_2_sentences_list[0], patent_2_sovs_list)
    d = time.time()
    print("比较时间：", d - c)

    # print(f'\nreview_opinion:\n{review_opinion}***\n')
    return review_opinion, words_info
    return review_opinion, words_info