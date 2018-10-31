#!/usr/bin/env python
from grammar.grammar import Grammar, first, follow, format_wordlist

G0 = Grammar(
	terminals    = [ "a", "b" ],
	nonterminals = [ "Z", "A" ],
	productions  = [
		("Z", [ "a", "A", "a", "b" ]),
		("Z", [ "b", "A", "b", "b" ]),
		("A", [ "a" ]),
		("A", [ ]),
	],
	start = "Z"
)
G1 = Grammar(
	terminals    = [ "(", ")" ],
	nonterminals = [ "S" ],
	productions  = [
		( "S", [ "S", "(", "S", ")", "S" ] ),
		( "S", [ ] ),
	],
	start        = "S"
)
G2 = Grammar(
	terminals = [],
	nonterminals = [ "A", "B", "C" ],
	productions = [
		("A", [ "B", "C" ]),
		("B", [ "C", "A" ]),
		("C", [ "A" ]),
	],
	start = "A"
)
G3 = Grammar(
	terminals    = [ "a", "b", "c" ],
	nonterminals = [ "S", "A" ],
	productions = [
		("S", [ "A", "a" ]),
		("A", [ "S", "b" ]),
		("A", [ "c" ]),
	],
	start = "S"
)
print G0
print "follow_3(A) = %s" % format_wordlist(follow(G0, 3, "A"))
print ""
print G1
print "follow_1(S) = %s" % format_wordlist(follow(G1, 1, "S"))
print ""
print G3
print "follow_2(A) = %s" % format_wordlist(follow(G3, 2, "A"))

print ""
print G0
print "first_0(Z) = %s" % format_wordlist(first(G0, 0, ["Z"]))
print "first_1(Z) = %s" % format_wordlist(first(G0, 1, ["Z"]))
print "first_2(Z) = %s" % format_wordlist(first(G0, 2, ["Z"]))
print "first_2(A) = %s" % format_wordlist(first(G0, 2, ["A"]))

assert len(first(G2, 0, ["A"])) == 0
assert len(first(G2, 5, ["A"])) == 0

G4 = Grammar(
	terminals    = [ "x", "y" ],
	nonterminals = [ "S" ],
	productions = [
		("S", [ "x", "S" ]),
	],
	start = "S"
)
print ""
print G4
print "first_10(S) = %s" % format_wordlist(first(G4, 10, ["S"]))

G5 = Grammar(
	terminals    = [ "x", "y" ],
	nonterminals = [ "S" ],
	productions = [
		("S", [ "S", "x" ]),
	],
	start = "S"
)
print ""
print G5
print "first_10(S) = %s" % format_wordlist(first(G5, 10, ["S"]))

G6 = Grammar(
	terminals    = [ "id", "+", "*", "(", ")" ],
	nonterminals = [ "E'", "E", "T", "F" ],
	productions = [
		("E'", ["E"]),
		("E",  ["T"]),
		("E",  ["E","+","T"]),
		("T",  ["F"]),
		("T",  ["T","*","F"]),
		("F",  ["(","E",")"]),
		("F",  ["id"])
	],
	start = "E'"
)
print ""
print G6
print "follow_1(E) = %s" % format_wordlist(follow(G6, 1, "E"))

G7 = Grammar(
	terminals    = [ "number", "+", "-", "*", "/", "(", ")" ],
	nonterminals = [ "E", "E'", "T", "T'", "F" ],
	productions = [
		("E",  ["T","E'"]),
		("E'", ["+","T","E'"]),
		("E'", ["-","T","E'"]),
		("E'", []),
		("T",  ["F","T'"]),
		("T'", ["*","F","T'"]),
		("T'", ["/","F","T'"]),
		("T'", []),
		("F",  ["(","E",")"]),
		("F",  ["number"])
	],
	start = "E"
)
print ""
print G7
for nonterminal in G7.nonterminals:
	print "first_1(%s) = %s" % (nonterminal, format_wordlist(first(G7, 1, [nonterminal])))
for nonterminal in G7.nonterminals:
	print "follow_1(%s) = %s" % (nonterminal, format_wordlist(follow(G7, 1, nonterminal)))
G8 = Grammar(
    terminals = ["(", ")", "*", "+", "id"],
    nonterminals = ["E", "E'", "F", "T", "T'"],
    productions = [
        ("E", ["T", "E'"]),
        ("E'", ["+", "T", "E'"]),
        ("E'", []),
        ("T", ["id"]),
        ("T", ["(", "E", ")"])
    ],
    start = "E"
)
print ""
print G8
for nonterminal in G8.nonterminals:
	print "first_3(%s) = %s" % (nonterminal, format_wordlist(first(G8, 3, [nonterminal])))
for nonterminal in G8.nonterminals:
	print "follow_3(%s) = %s" % (nonterminal, format_wordlist(follow(G8, 3, nonterminal)))
G9 = Grammar(
    terminals = ["(", ")"],
    nonterminals = ["E"],
    productions = [
        ("E", ["(", "E", ")"])
    ],
    start = "E"
)
print ""
print G9
print "first_1(E) = %s" % format_wordlist(first(G9, 1, ["E"]))
print "first_2(E) = %s" % format_wordlist(first(G9, 2, ["E"]))
