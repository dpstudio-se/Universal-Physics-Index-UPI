# UPI Global Research Workload v1

## Objective

Define a reproducible workload for mapping reachable, indexed and permitted open science research surfaces. It does not imply exhaustive access to the entire internet or restricted datasets.

## Research route

DISCOVERY -> OPEN RESEARCH INFRASTRUCTURE -> DATA / PAPERS / METHODS / SOFTWARE -> PROVENANCE -> UPI CLASSIFICATION -> MIRROR -> VERIFICATION -> UPI DNA

Candidate infrastructure layers include SUNET, SND, EOSC and GEANT plus international research and data networks. The source list is discovered dynamically and recorded with provenance.

## A -> O sweep

For each source/domain:
1. enumerate research objects;
2. normalize metadata without changing scientific meaning;
3. extract claims, equations, datasets, methods, measurements, code/software, references, dates and provenance;
4. classify EST / DER / HYP / SYM / ERR;
5. map into UPI domain chambers;
6. record dependencies and lineage.

## O -> A mirror sweep

Reverse the conceptual route:

domain -> model -> derivation -> claim -> source

Compare with:

source -> claim -> derivation -> model -> domain

If the reverse path cannot recover the source or assumptions, mark the relation incomplete.

## Sorting hierarchy

DOMAIN
SUBDOMAIN
SOURCE
STATUS
TIME
GEOGRAPHY
METHOD
EVIDENCE
PROVENANCE
DEPENDENCIES
CONFLICTS
REPRODUCIBILITY

## Evidence separation

Never merge observation with interpretation, correlation with causation, analogy with physical equivalence, historical statement with present day claim, legal text with legal interpretation, or open metadata with open underlying data.

## Self audit

UPI audits research and also audits the workload used to audit research.

WORKLOAD -> EXTRACT -> CLASSIFY -> CHAMBERS -> MIRROR -> VERIFY -> LOOP CHECK -> WORKLOAD UPDATE

## Loop termination

NEW NODE -> enqueue
CONFLICT -> review
KNOWN NODE -> reuse
DUPLICATE -> collapse with provenance
INSUFFICIENT EVIDENCE -> quarantine/review
Delta N = 0 -> stop frontier

## Capability gate

Before any source traversal, record:

CAPABILITY
TOOL
SKILL
ACCESS
INPUT CONTRACT
EXPECTED OUTPUT

A missing capability is recorded as an upstream dependency rather than misclassified as a downstream data or mathematical failure.

## Global coverage boundary

Whole network means the reachable, indexed and permitted research surface defined by current discovery. Private, restricted, paywalled or inaccessible material is not silently treated as absent.

## Output

Only verified and provenance complete candidates are promoted to UPI DNA. The active workload remains able to propose corrections without automatically promoting them to established knowledge.
