#!/usr/bin/env python

from pygraph.classes.graph import graph
from pygraph.readwrite.dot import write as write_graph

import sys
sys.path.append('..')
sys.path.append('/usr/lib/graphviz/python/')
sys.path.append('/usr/lib64/graphviz/python/')
import gv

rules = {
	'S\'': [['G']],
	'G': [['E', '=', 'E'], 'f'],
	'E': [['E', '+', 'T'], 'T'],
	'T': [['T', '*', 'f'], 'f'],
}

rules = {
	'ACCEPT': [['LIST']],
	'LIST': [['LIST', ',', 'ELEMENT'], ['ELEMENT']],
	'ELEMENT': [['a']],
}

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

def main():
	item_grps = []
	parent_grps = {}
	child_grps = {}
	repr2items = {}

	items = get_closure([Item('ACCEPT', rules['ACCEPT'][0], 0)])
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

			if new_items_repr not in parent_grps: parent_grps[new_items_repr] = []
			parent_grps[new_items_repr].append(items)

			if items_repr not in child_grps: child_grps[items_repr] = []
			child_grps[items_repr].append(new_items)

			if new_items != found_items: que.append(new_items)

	for items in item_grps:
		for item in items:
			print item
		print '----'

	for items_repr, childs in child_grps.iteritems():
		items = repr2items[items_repr]
		for child in childs:
			print '* %s => %s' % (items, child)

	gr = graph()
	gr.add_nodes(['a', 'b', 'c'])
	gr.add_edge(('a', 'b'))

	dot = write_graph(gr)
	gvv = gv.readstring(dot)
	gv.layout(gvv, 'dot')
	gv.render(gvv, 'png', 'test.png')

if __name__ == '__main__':
	main()
