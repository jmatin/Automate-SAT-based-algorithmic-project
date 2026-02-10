# Automate-SAT-based-algorithmic-project



## Project Overview

This project was developed in **October 2023** as part of a course project on
**automatic learning of string validation programs**.

The goal is to infer **finite automata** that validate strings based solely on
**positive and negative examples**, under the assumption that **simpler programs
(shorter automata)** provide better generalization.

---

## Problem Description

Given:
- An alphabet Σ
- A finite set of **positive examples** (accepted strings)
- A finite set of **negative examples** (rejected strings)

the objective is to automatically construct a **finite automaton** that:
- Accepts all positive examples
- Rejects all negative examples
- Uses the **smallest possible number of states**

This problem models the task of learning validation programs (e.g., email
validators) when only examples are available and no formal specification is given.

---

## Approach

The project models automaton synthesis as a **Boolean satisfiability (SAT) problem**.

Key ideas include:
- Encoding automaton structure (states, transitions, accepting states) as
  **propositional variables**
- Expressing correctness constraints (consistency with examples) as
  **CNF formulas**
- Using the **PySAT** library to solve the resulting SAT instances
- Reconstructing valid automata from satisfying assignments

---

## Implemented Features

The project includes algorithms to:
- Generate a deterministic finite automaton (DFA) with at most *k* states
- Compute a **minimal DFA** consistent with the examples
- Enforce additional constraints:
  - Completeness
  - Reversibility
  - Bounded number of accepting states
- Extend the approach to **non‑deterministic finite automata (NFA)**

All solutions are implemented in **Python 3**, using only the allowed libraries:
- `pysat`
- `automata`

---

## Deliverables

- `project.py` — Implementation of all required algorithms
- A **scientific report** (LaTeX / Typst, PDF + source) explaining:
  - The SAT encodings
  - Theoretical justification
  - Algorithmic choices
- A **README** with execution instructions

---

## Key Concepts

- Finite automata (DFA & NFA)
- Boolean satisfiability (SAT)
- Constraint encoding
- Program synthesis from examples
- Model minimality and generalization

---
