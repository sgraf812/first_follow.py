# coding=utf-8
# vim:tabstop=4:softtabstop=4:shiftwidth=4:noexpandtab
# Types for specifying context free grammars with functions to calculate
# first and follow sets
EOF_CHAR = "#"

# Part1: Grammars
def hash_list(list):
	hashed_elements = map(hash, list)
	return reduce(lambda x, y:x^y, hashed_elements, 0)

# A Production is just a python tuple: (nonterminal, list-of-replacements),
# the list-of-replacements is a normal python list of terminals or nonterminals.
# The only reason this is modeled as a separate class is because we need a hash
# function (which python doesn't provide for lists...)
class Production(tuple):
	def __new__(cls, (left, right)):
		return tuple.__new__(cls, (left, right))
	def __hash__(self):
		return hash(self[0]) ^ hash_list(self[1])
	def __str__(self):
		(left, right) = self
		res = "%s →" % left
		if len(right) == 0:
			res += " ε"
		else:
			for e in right:
				res += " %s" % e
		return res

# A Grammar consists of:
#  - (a list of) terminals
#  - (a list of) nonterminals
#  - (a list of) productions
#  - (the) start (nonterminal)
class Grammar:
	def __init__(self, terminals, nonterminals, productions, start):
		self.terminals    = terminals
		self.nonterminals = nonterminals
		if not isinstance(productions[0], Production):
			productions = map(Production, productions)
		self.productions  = productions
		self.start        = start
		# Check if components of the productions are terminals/nonterminals
		for p in productions:
			assert p[0] in nonterminals
			for r in p[1]:
				assert r in terminals or r in nonterminals

	def __str__(self):
		res  = "Terminals: %s\n" % self.terminals
		res += "NonTerminals: %s\n" % self.nonterminals
		res += "Productions:\n"
		for production in self.productions:
			res += "\t%s\n" % (production,)
		res += "Start: %s" % self.start
		return res

# Create an augmented grammar
def augment(grammar):
	newStart = grammar.start
	while newStart in grammar.nonterminals or newStart in grammar.terminals:
		newStart += "'"
	return Grammar(
		terminals    = grammar.terminals,
		nonterminals = grammar.nonterminals + [newStart],
		productions  = [ (newStart, [grammar.start]) ] + grammar.productions,
		start        = newStart)

class SymList(list):
	def __new__(cls, list=[]):
		return list.__new__(cls, list)
	def __hash__(self):
		return hash_list(self)

epsilon = SymList()

def k_concat(k, l, r):
	"""
	Computes the k-concatenation of two words (e.g. SymList of terminals).
	It's concatenation where the result is truncated to be at most k
	terminals long.
	"""
	return SymList((l + r)[:k])

def first_no_eof(grammar, k, sequence):
	"""
	Computes the first_k set of the given sequence of the vocabulary
	by solving the set recurrence from Wilhelm, Seidl and Hack.
	"""
	# table: nonterminal -> set of SymList (first_k of nonterminal)
	table = dict((nt, set()) for nt in grammar.nonterminals)

	# This will get the (current approximation of) the first_k set
	# for a single symbol
	def get_first(s):
		if s in grammar.terminals:
			return {SymList([s])}
		else:
			assert s in grammar.nonterminals
			return table[s]

	def iter(k, seq):
		firsts = map(get_first, seq)
		# Now reduce them with k-concatenation over the powersets.
		# We can stop as soon as there are no more terminal
		# sequences in words that are of length less than k.
		# The default, used for i.e. empty production rules,
		# is the singleton set with the epsilon word.
		words = {epsilon}
		# complete_words stores words of length k.
		# These are left absorbing elements of k-concatenation.
		complete_words = set()
		for first in firsts:
			if len(words) == 0:
				break
			longer_words = set()
			for w in words:
				for f in first:
					new_word = k_concat(k, w, f)
					if len(new_word) < k:
						longer_words.add(new_word)
					else:
						assert len(new_word) == k
						complete_words.add(new_word)
			words = longer_words
		return words.union(complete_words)

	# Now iterate iter on every table entry until we reach a
	# fixed-point
	changed = True
	while changed:
		changed = False
		for (nt, seq) in grammar.productions:
			old = table[nt]
			new = old.union(iter(k, seq))
			table[nt] = new
			changed = changed or new != old

	# Now that we resolved the 'dynamic program' (+ recursion)
	return iter(k, sequence)

def first(grammar, k, sequence):
	# Just pad with EOF
	return set(SymList(w + (k - len(w))*[EOF_CHAR])
				for w in first_no_eof(grammar, k, sequence))

def follow(grammar, k, nonterminal):
	# This formulation only works for augmented grammars.
	grammar = augment(grammar)

	assert nonterminal in grammar.nonterminals

	# table: nonterminal -> set of SymList (follow_k of nonterminal)
	table = dict((nt, set()) for nt in grammar.nonterminals)

	# This should be enough to propagate EOFs throughout all follow sets.
	table[grammar.start] = set([SymList(k*[EOF_CHAR])])

	def iter(k, parent_nt, right):
		"""
		Takes the parent non-terminal (Y below) and the sequence right (b)
		to the non-terminal occurrence X for which we want to compute part
		of the follow set.

		Iterate this for every production X -> aYb.
		"""
		words = set()
		for a in first_no_eof(grammar, k, right):
			for b in table[parent_nt]:
				words.add(k_concat(k, a, b))
		return words

	# Now iterate iter on every table entry until we reach a
	# fixed-point
	changed = True
	while changed:
		changed = False
		for (parent_nt, seq) in grammar.productions:
			for i in range(0, len(seq)):
				if seq[i] in grammar.terminals:
					continue

				# Re-iterate the follow the set for the non-terminal occ
				nt = seq[i]
				if nt == grammar.start:
					# Already handled by initialising the table
					continue

				old = table[nt]
				new = old.union(iter(k, parent_nt, seq[i+1:]))
				#print("nt: %s, old: %s, new: %s, parent: %s, seq: %s, beta: %s" % (nt, old, new, parent_nt, seq, seq[i+1:]))
				table[nt] = new
				changed = changed or new != old

	return table[nonterminal]

def format_wordlist(words):
	formated = []
	one_char_mode = True
	for word in words:
		for t in word:
			if len(str(t)) != 1:
				one_char_mode = False

	for word in words:
		if len(word) == 0:
			formated.append("ε")
			continue
		res = ""
		sep = ""
		for w in word:
			res += sep
			if not one_char_mode:
				sep = " "
			res += str(w)
		formated.append(res)
	return "{" + ", ".join(formated) + "}"
