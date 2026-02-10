from utils import *
from tests import *

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from pysat.solvers import Minisat22, Minicard
from pysat.formula import CNF, CNFPlus, IDPool


def determined(cnf, alphabet, k, vpool):
    # Contrainte 1
    # T(q,l,q_) implique non T(q,l,q__)
    for l in alphabet:
        for q in range(k):
            for q_ in range(k):
                for q__ in range(k):
                    if q_ != q__:
                        cnf.append([-vpool.id((q, l, q_)), -vpool.id((q, l, q__))])

def unique_execution(vpool, cnf, m, k):
    # Contrainte 3

    # E(m, n, q) vraie pour au moins un q
    for n in range(len(m) + 1):
        d = []
        for q in range(k):
            d.append(vpool.id((m, n, q)))
        cnf.append(d)

    # E(m, n, q) vraie pour au plus un q
    au_plus_execution(vpool, cnf, m, k)

def au_plus_execution(vpool, cnf, m, k):
    # Contrainte 4
    for n in range(len(m) + 1):
        for v in range(k):
            for w in range(k):
                if v != w:
                    cnf.append([-vpool.id((m, n, v)), -vpool.id((m, n, w))])

def execution_continue(vpool, cnf, m, k):
    # Contrainte 5
    for n in range(len(m)):
        for q in range(k):
            for p in range(k):
                cnf.append([-vpool.id((m, n, q)), -vpool.id((q, m[n], p)), vpool.id((m, n + 1, p))])

def existence_transition(m, k, vpool, cnf):
    # Contrainte 6
    for n in range(len(m)):
        for i in range(k):
            E = [-vpool.id((m, n, i))]
            for j in range(k):
                E.append(vpool.id((i, m[n], j)))
            cnf.append(E)

def dernier_acceptant(m, vpool, k, cnf):
    # Contrainte 7
    # Le dernier état est acceptant.
    for q in range(k):
        cnf.append([-vpool.id((m, len(m), q)), vpool.id(q)])

def dernier_non_acceptant(m, vpool, k, cnf):
    # Contrainte 8
    # Le dernier état n'est pas acceptant.
    for q in range(k):
        cnf.append([-vpool.id((m, len(m), q)), -vpool.id(q)])

def complete(alphabet, k, vpool, cnf):
    """
    Fonction qui vérifie la complétude d'un automate
    """
    for n in alphabet:
        for q in range(k):
            E = []
            for p in range(k):
                E.append(vpool.id((q, n, p)))
            cnf.append(E)

def reversibility(alphabet, k, vpool, cnf):
    """
    Fonction qui vérifie la réversibilité d'un automate
    """
    # Contrainte 10
    for l in alphabet:
        for q in range(k):
            for q_ in range(k):
                for q__ in range(k):
                    if q_ != q__:
                        cnf.append([-vpool.id((q_, l, q)), -vpool.id((q__, l, q))])

def création_automate_déterministe(alphabet, vpool, solveur, k):
    """
    Fonction qui retourne un automate de k états déterministe sur un alphabet grâce à un solveur
    """
    states = {0}
    finalStates = set()
    initialState = 0
    sigma = set(alphabet)
    transitions = {}

    # Ajout de l'état initial
    states.add(initialState)

    # Création de l'ensemble F
    for q in range(k):
        if vpool.id(q) in solveur.get_model():
            finalStates.add(q)
            states.add(q)

    # Création de la fonction de transition
    for l in alphabet:
        for q in range(k):
            for q_ in range(k):
                if vpool.id((q, l, q_)) in solveur.get_model():
                    states.add(q)
                    states.add(q_)
                    if q not in transitions:
                        transitions[q] = {}
                    if q_ not in transitions:
                        transitions[q_] = {}
                    transitions[q][l] = q_

    # L'état initial a une transition définie
    if initialState not in transitions:
        transitions[initialState] = {}

    # Créer l'automate
    dfa = DFA(states=states, input_symbols=sigma, transitions=transitions, initial_state=initialState,
              final_states=finalStates, allow_partial=True)
    return dfa

def non_determined(cnf, alphabet, k, vpool):
    pass
def création_automate_non_déterministe(alphabet, vpool, solveur, k):
    """
    Fonction qui retourne un automate de k états non-déterministe sur un alphabet grâce à un solveur
    """
    states = {0}
    finalStates = set()
    initialState = 0
    sigma = set(alphabet)
    transitions = {}

    # Ajout de l'état initial
    states.add(initialState)

    # Création de l'ensemble F
    for q in range(k):
        if vpool.id(q) in solveur.get_model():
            finalStates.add(q)

    # Création de la fonction de transition
    for l in alphabet:
        for q in range(k):
            for q_ in range(k):
                if vpool.id((q, l, q_)) in solveur.get_model():
                    states.add(q)
                    states.add(q_)
                    if q not in transitions:
                        transitions[q] = {}
                    if l not in transitions[q]:
                        transitions[q][l] = set()
                    transitions[q][l].add(q_)

    # Ajout des états sans transition sortante
    for q in states:
        if q not in transitions:
            transitions[q] = {}

    # L'état initial a une transition définie
    if initialState not in transitions:
        transitions[initialState] = {}

    # Créer l'automate non déterministe
    nfa = NFA(states=states, input_symbols=sigma, transitions=transitions, initial_state=initialState,
              final_states=finalStates)

    return nfa

# Q2
def gen_aut(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    vpool = IDPool(start_from=1)

    cnf = CNF()

    determined(cnf, alphabet, k, vpool)

    # Positif
    for m in pos:
        cnf.append([vpool.id((m, 0, 0))])  # Contrainte 2

        unique_execution(vpool, cnf, m, k)

        execution_continue(vpool, cnf, m, k)

        existence_transition(m, k, vpool, cnf)

        dernier_acceptant(m, vpool, k, cnf)

    # Négatif
    for m in neg:
        cnf.append([vpool.id((m, 0, 0))])  # Contrainte 2

        au_plus_execution(vpool, cnf, m, k)

        execution_continue(vpool, cnf, m, k)

        dernier_non_acceptant(m, vpool, k, cnf)

    # Résolution
    solveur = Minisat22(use_timer=True)
    solveur.append_formula(cnf.clauses, no_return=False)
    solve = solveur.solve()

    # Construction de l'automate
    if solve:
        return création_automate_déterministe(alphabet, vpool, solveur, k)

# Q3
def gen_minaut(alphabet: str, pos: list[str], neg: list[str]) -> DFA:
    k = 0
    while gen_aut(alphabet, pos, neg, k) == None:
        k += 1
    return gen_aut(alphabet, pos, neg, k)

# Q4
def gen_autc(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    vpool = IDPool(start_from=1)

    cnf = CNF()

    determined(cnf, alphabet, k, vpool)

    complete(alphabet, k, vpool, cnf)

    # Positif
    for m in pos:
        cnf.append([vpool.id((m, 0, 0))])  # Contrainte 2

        unique_execution(vpool, cnf, m, k)

        execution_continue(vpool, cnf, m, k)

        existence_transition(m, k, vpool, cnf)

        dernier_acceptant(m, vpool, k, cnf)

    # Négatif
    for m in neg:
        cnf.append([vpool.id((m, 0, 0))])  # Contrainte 2

        au_plus_execution(vpool, cnf, m, k)

        execution_continue(vpool, cnf, m, k)

        dernier_non_acceptant(m, vpool, k, cnf)

    # Résolution
    solveur = Minisat22(use_timer=True)
    solveur.append_formula(cnf.clauses, no_return=False)
    solve = solveur.solve()

    # Construction de l'automate
    if solve:
        return création_automate_déterministe(alphabet, vpool, solveur, k)


# Q5
def gen_autr(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    vpool = IDPool(start_from=1)

    cnf = CNF()

    determined(cnf, alphabet, k, vpool)

    reversibility(alphabet, k, vpool, cnf)

    # Positif
    for m in pos:
        cnf.append([vpool.id((m, 0, 0))]) # Contrainte 2

        unique_execution(vpool, cnf, m, k)

        execution_continue(vpool, cnf, m, k)

        existence_transition(m, k, vpool, cnf)

        dernier_acceptant(m, vpool, k, cnf)

    # Négatif
    for m in neg:
        cnf.append([vpool.id((m, 0, 0))]) # Contrainte 2

        au_plus_execution(vpool, cnf, m, k)

        execution_continue(vpool, cnf, m, k)

        dernier_non_acceptant(m, vpool, k, cnf)

    # Résolution
    solveur = Minisat22(use_timer=True)
    solveur.append_formula(cnf.clauses, no_return=False)
    solve = solveur.solve()

    # Construction de l'automate
    if solve:
        return création_automate_déterministe(alphabet, vpool, solveur, k)

# Q6
def gen_autcard(alphabet: str, pos: list[str], neg: list[str], k: int, ell: int) -> DFA:
    vpool = IDPool(start_from=1)

    cnf = CNF()

    etat_acceptant = []

    determined(cnf, alphabet, k, vpool)

    # Positif
    for m in pos:
        cnf.append([vpool.id((m, 0, 0))]) # Contrainte 2

        unique_execution(vpool, cnf, m, k)

        execution_continue(vpool, cnf, m, k)

        existence_transition(m, k, vpool, cnf)

        dernier_acceptant(m, vpool, k, cnf)

    # Négatif
    for m in neg:
        cnf.append([vpool.id((m, 0, 0))]) # Contrainte 2

        au_plus_execution(vpool, cnf, m, k)

        execution_continue(vpool, cnf, m, k)

        dernier_non_acceptant(m, vpool, k, cnf)

    # Cardinalité
    for q in range(k):
        if vpool.id(q):
            etat_acceptant.append(vpool.id(q))

    # Résolution
    solveur = Minicard(use_timer=True)
    solveur.append_formula(cnf.clauses, no_return=False)
    solveur.add_atmost(etat_acceptant, ell)
    solve = solveur.solve()

    # Construction de l'automate
    if solve:
        return création_automate_déterministe(alphabet, vpool, solveur, k)

# Q7
def gen_autn(alphabet: str, pos: list[str], neg: list[str], k) -> NFA:
    vpool = IDPool(start_from=1)
    cnf = CNF()
    non_determined(cnf, alphabet, k, vpool)

    # Positif
    for m in pos:
        cnf.append([vpool.id((m, 0, 0))]) # Contrainte 2

        execution_continue(vpool, cnf, m, k)

        existence_transition(m, k, vpool, cnf)

        dernier_acceptant(m, vpool, k, cnf)

    # Négatif
    for m in neg:
        cnf.append([vpool.id((m, 0, 0))]) # Contrainte 2

        execution_continue(vpool, cnf, m, k)

        dernier_non_acceptant(m, vpool, k, cnf)

    # Résolution
    solveur = Minisat22(use_timer=True)
    solveur.append_formula(cnf.clauses, no_return=False)
    solve = solveur.solve()
    # Construction de l'automate non déterministe
    if solve:
        return création_automate_non_déterministe(alphabet, vpool, solveur, k)

def main():
    test_aut()
    test_minaut()
    test_autc()
    test_autr()
    test_autcard()
    test_autn()


if __name__ == '__main__':
    main()