#! /usr/bin/env python
# -*- coding: utf-8 -*-
from json import load
from json import dumps
from pymystem3 import Mystem
from rutermextract import TermExtractor as TE
from nltk.tokenize import WordPunctTokenizer as WPT
import pymorphy2

# Парсим текст. На вход подается текст.
def tokenize(sentences):
	arr = []
	morph = pymorphy2.MorphAnalyzer()
	term_extractor = TermExtractor()
	for sent in nltk.sent_tokenize(sentences.lower()):
		for term in term_extractor(sent):
			arr.append(term.normalized)
			print (term.normalized, term.count)
		for word in nltk.word_tokenize(sent):
			p = morph.parse(word)[0]
			v = p.tag.POS
			if v == 'VERB':
				arr.append(word)
				print (word)
	return arr

# Попытка поиска однородных членов предложения
def odnorodn(term, v):
	if v == 'ADJF' or v == 'ADJS' or v == 'ADVB':
		if v in term:
			print (v)

def compare_phrase(P1, P2):
	word_tokenizer = WPT()

	words1 = word_tokenizer.tokenize(P1)
	words2 = word_tokenizer.tokenize(P2)

	P = 1.0
	for i in range(max(len(words1),len(words2))):
		p = {-1:1, 0:1, 1:1}
		for j in p.keys():
			try:
				p[j] *= compare(words1[i], words2[i+j])
			except IndexError:
				p[j] = 0
		P *= max(p.values())

	return P

def compare(S1,S2):
	ngrams = [S1[i:i+3] for i in range(len(S1))]
	count = 0
	for ngram in ngrams:
		count += S2.count(ngram)

	return count/max(len(S1), len(S2))

def load_data(filename = 'data.json'):
	mystem = Mystem()
	knowledge = {}
	significats = {}
	try:
		kb = load(open(filename))
		for _ in kb.keys():
			pairs = kb[_]
			for pair in pairs:
				d1 = pair['denotat1']
				d2 = pair['denotat2']
				rl = pair['relation']
				lnk = ()
				for d in [d1, rl, d2]:
					key = ''
					val = []
					prt = ''
					for a in mystem.analyze(d):
						try:
							key += a['analysis'][0]['lex']
							val += a['analysis']
							prt += a['analysis'][0]['lex']
						except KeyError:
							key += a['text']
							prt += a['text']
						except IndexError:
							key += a['text']
							prt += a['text']
					significats.update({key.strip('\n'):val})
					lnk += tuple([prt.strip('\n')])
				try:
					knowledge[lnk] += 1
				except KeyError:
					knowledge.update({lnk:1})
	except FileNotFoundError as fnfe:
		pass
	return [significats, knowledge]

def load_q(filename = 'test.json'):
	try:
		return load(open(filename))
	except FileNotFoundError as fnfe:
		return {}

def load_key(filename = 'key.json'):
	try:
		return load(open(filename))
	except FileNotFoundError as fnfe:
		return {}

def check_key(ans, key):
	c = 0
	w = 0
	for q in key.keys():
		e = False
		for a in key[q].keys():
			if key[q][a] != ans[q][a][0]:
				print(q, "\n", key[q], ans[q])
				e = True
		if e:
			w += 1
		else:
			c += 1
	print(c, w)

def answer(knowledge = {}, questions = {}):
	mystem = Mystem()
	term_extractor = TE()

	def is_negative(text):
		for a in mystem.analyze(text):
			for rez in get_analysis(a):
				if (rez['gr'] == 'PART=' and rez['lex'] == 'не'):
					return -1
		return 1

	def get_analysis(mystem_result):
			try:
				return mystem_result['analysis']
			except KeyError:
				return []


	def get_significat_keys(terms):
		significat_keys = ()
		for term in terms:
			significat_key = ''
			for analysis in mystem.analyze(term):
				for rez in get_analysis(analysis):
					try:
						significat_key += rez['lex'] + " "
					except KeyError:
						significat_key += rez['text'] + " "
			significat_keys += tuple([significat_key.strip()])
		return significat_keys

	def get_real_keys(significat_keys):
		real_keys = []
		for search_key in significat_keys:
			for real_key in knowledge[0].keys():
				k = compare_phrase(search_key, real_key)
				if k > 0.55:
					real_keys += [real_key]

		return real_keys

	def find_kb_keys(real_keys):
		found_keys = []
		found_keys = []
		for rel in knowledge[1].keys():
			for key in real_keys:
				try:
					rel.index(key)
					found_keys += [rel]
				except ValueError:
					pass
			if len(found_keys) >= len(real_keys):
				break
		return found_keys

	ans = {}
	for q in questions.keys():
		ans.update({q:{}})
		for a in questions[q].keys():
			text = q + ' ' + questions[q][a]
			terms = [str(term) for term in term_extractor(text)]
			neg = is_negative(text)
			significat_keys = get_significat_keys(terms)
			real_keys = get_real_keys(significat_keys)
			found_keys = find_kb_keys(real_keys)
			# print("%s) %s\n%s\nt %s\nsk %s\nrk %s\nfk %s" % (a, text, neg, terms, significat_keys, real_keys, found_keys))


			ans[q].update({a:[neg * len(found_keys), questions[q][a], found_keys]})
			#.update({})
		max = ['', -100]
		for a in ans[q].keys():
			if ans[q][a][0] > max[1]:
				max[1] = ans[q][a][0]
				max[0] = a
		for a in ans[q].keys():
			if a == max[0]:
				ans[q][a][0] = 1
			else:
				ans[q][a][0] = 0
		# print(max)
	return ans

def to_graph(data):
	with open('graph.dot', 'w') as g:
		g.write('digraph g {\n')
		for k in data.keys():
			g.write('"%s" -> "%s" [label="%s"]' % (k[0], k[2], k[1]))
		g.write('}\n')
		g.close()

if __name__ == '__main__':
	import sys
	data = load_data('data.json')
	to_graph(data[1])
	q = load_q('test.json')
	a = answer(data,q)
	print(dumps(a, indent = 4, ensure_ascii = 0))
	k = load_key('key.json')
	check_key(a, k)
	# Вызов парсера
	tokenize(u'Красивая и загадочная Оля написала и отправила мне длинное и информативное сообщение и письмо.')
