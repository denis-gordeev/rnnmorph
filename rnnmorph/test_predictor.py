import unittest
import logging
import sys
import numpy as np

# import os
# os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
# os.environ["CUDA_VISIBLE_DEVICES"] = ""

from rnnmorph.predictor import RNNMorphPredictor
from rnnmorph.tag_genres import tag_ru_files, tag_en_files


class TestLSTMMorph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        cls.en_predictor = RNNMorphPredictor(language="en")
        cls.ru_predictor = RNNMorphPredictor(language="ru")

    def __assert_parse(self, parse, pos, normal_form, tag):
        self.assertEqual(parse.pos, pos)
        self.assertEqual(parse.normal_form, normal_form)
        self.assertEqual(parse.tag, tag)

    def test_ru_sentence_analysis1(self):
        forms = self.ru_predictor.predict_sentence_tags(["косил", "косой", "косой", "косой"])
        self.__assert_parse(forms[0], 'VERB', 'косить',
                            'Gender=Masc|Mood=Ind|Number=Sing|Tense=Past|VerbForm=Fin|Voice=Act')
        self.assertIn(1, forms[0].vector)
    
    def test_empty_sentence(self):
        forms = self.ru_predictor.predict_sentence_tags([])
        self.assertEqual(forms, [])

    def test_ru_sentence_analysis2(self):
        forms = self.ru_predictor.predict_sentence_tags(["мама", "мыла", "раму"])
        self.__assert_parse(forms[0], 'NOUN', 'мама', 'Case=Nom|Gender=Fem|Number=Sing')
        self.__assert_parse(forms[1], 'VERB', 'мыть',
                            'Gender=Fem|Mood=Ind|Number=Sing|Tense=Past|VerbForm=Fin|Voice=Act')
        self.__assert_parse(forms[2], 'NOUN', 'рама', 'Case=Acc|Gender=Fem|Number=Sing')

    def test_ru_sentences_analysis1(self):
        forms = self.ru_predictor.predict_sentences_tags([["косил", "косой", "косой", "косой"], ["мама", "мыла", "раму"]])

        self.__assert_parse(forms[0][0], 'VERB', 'косить',
                            'Gender=Masc|Mood=Ind|Number=Sing|Tense=Past|VerbForm=Fin|Voice=Act')

        self.__assert_parse(forms[1][0], 'NOUN', 'мама', 'Case=Nom|Gender=Fem|Number=Sing')
        self.__assert_parse(forms[1][1], 'VERB', 'мыть',
                            'Gender=Fem|Mood=Ind|Number=Sing|Tense=Past|VerbForm=Fin|Voice=Act')
        self.__assert_parse(forms[1][2], 'NOUN', 'рама', 'Case=Acc|Gender=Fem|Number=Sing')
    
    def test_empty_sentences(self):
        forms = self.ru_predictor.predict_sentences_tags([[]])
        self.assertEqual(forms, [[]])
        
    def test_ru_one_empty_sentence_in_sentences(self):
        forms = self.ru_predictor.predict_sentences_tags([["косил", "косой", "косой", "косой"], []])
        self.assertEqual(forms[1], [])
        self.assertNotEqual(forms[0], [])

    def test_ru_proba(self):
        forms = self.ru_predictor.predict_sentence_tags_proba(["косил", "косой", "косой", "косой"])
        for word_proba in forms:
            self.assertEqual(len(word_proba), 252)
        indices = np.array([pair[0] for pair in forms[2]]).argsort()[-5:][::-1]
        variants = [forms[2][i][1].tag for i in indices]
        self.assertIn('Case=Nom|Degree=Pos|Gender=Masc|Number=Sing', variants)

    def test_ru_genres_accuracy(self):
        quality = tag_ru_files(self.ru_predictor)
        self.assertGreater(quality['Lenta'].tag_accuracy, 95)
        self.assertGreater(quality['Lenta'].sentence_accuracy, 70)
        self.assertGreater(quality['VK'].tag_accuracy, 93)
        self.assertGreater(quality['VK'].sentence_accuracy, 65)
        self.assertGreater(quality['JZ'].tag_accuracy, 94)
        self.assertGreater(quality['JZ'].sentence_accuracy, 70)
        print("Точность по тегам по всем разделам: %.2f%%" % (quality['All']['tag_accuracy']*100))
        print("Точность по предложениям по всем разделам: %.2f%%" % (quality['All']['sentence_accuracy'] * 100))
        self.assertGreater(quality['All']['tag_accuracy'], 0.95)

    # def test_en_accuracy(self):
    #     print(tag_en_files(self.en_predictor))