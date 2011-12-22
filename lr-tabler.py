#!/usr/bin/env python

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

rules = {
	'S\'': [['G']],
	'G': [['E', '=', 'E'], 'f'],
	'E': [['E', '+', 'T'], 'T'],
	'T': [['T', '*', 'f'], 'f'],
}
st_sym = 'S\''

rules = {
	'ACCEPT': [['LIST']],
	'LIST': [['LIST', ',', 'ELEMENT'], ['ELEMENT']],
	'ELEMENT': [['a']],
}
st_sym = 'ACCEPT'

rules = {
	'E\'': [['E']],
	'E': [['E', '+', 'T'], ['T']],
	'T': [['T', '*', 'F'], ['F']],
	'F': [['(', 'E', ')'], ['id']],
}
st_sym = 'E\''

rules = {
	'S\'': [['S']],
	'S': [['L', '=', 'R'], ['R']],
	'L': [['*', 'R'], ['id']],
	'R': [['L']],
}
st_sym = 'S\''

class Item:
	st = None
	syms = []
	idx = -1

	def __init__(self, st, syms, idx):
		self.st = st
		self.syms = syms
		self.idx = idx

	def __repr__(self):
		output = '%s => ' % self.st

		for i, sym in enumerate(self.syms):
			if i == self.idx: output += '.'
			output += sym+' '

		if self.idx == len(self.syms): output += '.'

		return '(%s)' % output.rstrip()

def get_closure(items):
	que = list(items)
	res = []

	visit = {}

	while que:
		item = que.pop()
		res.append(item)

		if item.idx == len(item.syms): continue
		sym = item.syms[item.idx]
		if sym in visit: continue
		visit[sym] = True

		if sym in rules:
			for syms in rules[sym]:
				que.append(Item(sym, syms, 0))

	return res

def get_goto(items, sym):
	return get_closure(Item(x.st, x.syms, x.idx+1) for x in items if x.idx != len(x.syms) and x.syms[x.idx] == sym)

def get_items_str(items):
	res = ''

	for item in items:
		res += repr(item)+'\n'

	return res.rstrip()

def main():
	item_grps = []
	parent_grp_grps = {}
	child_grp_grps = {}
	repr2items = {}

	items = get_closure([Item(st_sym, rules[st_sym][0], 0)])
	repr2items[repr(items)] = items

	que = [items]

	while que:
		items = que.pop()
		items_repr = repr(items)

		item_grps.append(items)

		syms = {}
		for item in items:
			if item.idx == len(item.syms): continue
			syms[item.syms[item.idx]] = None

		for sym in syms:
			new_items = get_goto(items, sym)
			new_items_repr = repr(new_items)

			found_items = repr2items.get(new_items_repr, None)
			if found_items: new_items = found_items
			else: repr2items[new_items_repr]  = new_items

			if new_items_repr not in parent_grp_grps: parent_grp_grps[new_items_repr] = []
			parent_grp_grps[new_items_repr].append([items, sym])

			if items_repr not in child_grp_grps: child_grp_grps[items_repr] = []
			child_grp_grps[items_repr].append([new_items, sym])

			if new_items != found_items: que.append(new_items)

	for items in item_grps:
		for item in items:
			print item
		print '----'

	for items_repr, child_grps in child_grp_grps.iteritems():
		items = repr2items[items_repr]
		for childs, sym in child_grps:
			print '* %s => %s' % (items, childs)

	gr = nx.DiGraph()

	for items_repr, child_grps in child_grp_grps.iteritems():
		items = repr2items[items_repr]

		items_str = get_items_str(items)

		for childs, sym in child_grps:
			childs_str = get_items_str(childs)
			gr.add_edge(items_str, childs_str, label=sym)

	pos = nx.spring_layout(gr)
	nx.draw(gr, pos)
	nx.draw_networkx_edge_labels(gr, pos, node_size=100)
	plt.axis('off')
	fig = plt.gcf()
	fig.set_size_inches(10, 10)
	plt.savefig('test.png')

if __name__ == '__main__':
	main()
