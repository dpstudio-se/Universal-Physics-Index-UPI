"""TF (Tryckfrihetsforordningen) review-routing and public-document flow.

Implements, as real executable code, the "Loop C/D/E/F" routing graph from
the user-supplied Omega1766 workload spec:

* Loop C (BOUNDARY): TF 1:7-1:10 gates (acquire, pre-block, exclusive, interpret).
* Loop D (DOCUMENT): TF 2:3-2:19 public-document disclosure pipeline.
* Loop E/F (ERROR/REVIEW + CLOSED-FEEDBACK): the KU / JO / JK / DOMSTOL router.

Every fact encoded here (paragraph numbers, which body reviews which actor)
is EST only insofar as it has been checked against a primary or
near-primary source; this module does not itself constitute legal advice,
and does not decide whether any *specific* real-world act violates TF -- it
only encodes the routing/classification structure so that a specific case
can be tested against it (see docs on burden of proof in
:mod:`upi.omega1766_transparency`).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ReviewBody(str, Enum):
    """Who reviews what. See RF 13:1 (KU), RF 13:6 (JO), TF 9:1-3 (JK)."""

    KU = "KU"  # Konstitutionsutskottet: regering/statsrad (RF 13:1-3)
    JO = "JO"  # Justitieombudsmannen: myndighet/domstol/tjansteman (RF 13:6)
    JK = "JK"  # Justitiekanslern: sole prosecutor for TF/YGL offences (TF 9:1-3)
    DOMSTOL = "DOMSTOL"  # Appealable disclosure refusal (TF 2:19, OSL 6:3)


class ActorKind(str, Enum):
    REGERING_STATSRAD = "regering/statsrad"
    MYNDIGHET_DOMSTOL_TJANSTEMAN = "myndighet/domstol/tjansteman"
    TF_BROTT = "tryckfrihetsbrott"
    OVERKLAGBART_UTLAMNANDE = "overklagbart_utlamnandebeslut"


# JO-instruktionen (1986:765, tidigare 1975:1345), 15 §: regeringen/statsrad
# star INTE under JO:s tillsyn -- explicit exclusion, not an oversight gap.
JO_EXCLUDES_GOVERNMENT = True


def route_review(actor: ActorKind) -> ReviewBody:
    """R(x) from the spec: map an actor/situation kind to its review body.

    This is a pure lookup, not a judgment about guilt; it only answers
    "which body has jurisdiction to review this kind of actor/situation".
    """
    mapping = {
        ActorKind.REGERING_STATSRAD: ReviewBody.KU,
        ActorKind.MYNDIGHET_DOMSTOL_TJANSTEMAN: ReviewBody.JO,
        ActorKind.TF_BROTT: ReviewBody.JK,
        ActorKind.OVERKLAGBART_UTLAMNANDE: ReviewBody.DOMSTOL,
    }
    return mapping[actor]


def assert_jo_jurisdiction(actor: ActorKind) -> None:
    """Guard against the named Odin's Eye mistake: ALL PUBLIC ERROR -> JO.

    Raises if a caller tries to route a government/statsrad matter to JO,
    since JO-instr. 15 SS explicitly excludes them.
    """
    if actor is ActorKind.REGERING_STATSRAD and JO_EXCLUDES_GOVERNMENT:
        raise ValueError(
            "regering/statsrad is excluded from JO oversight (JO-instr. 15 SS); "
            "route to KU (RF 13:1-3) instead"
        )


class DocumentGateStatus(str, Enum):
    NOT_A_DOCUMENT = "NOT_A_DOCUMENT"  # fails TF 2:3
    NOT_PUBLIC = "NOT_PUBLIC"  # fails TF 2:4 (not stored+received/drawn-up)
    EXCLUDED = "EXCLUDED"  # TF 2:12-14 (drafts, memoranda, etc.)
    SECRET = "SECRET"  # blocked by TF 2:2 secrecy gate (needs statutory basis)
    DISCLOSABLE = "DISCLOSABLE"


@dataclass(frozen=True)
class DocumentCandidate:
    """Loop D input: DATA -> HANDLING? -> FORVARAD? -> INKOMMEN/UPPRATTAD? -> ALLMAN? -> SEKRETESS? -> UTLAMNA."""

    is_handling: bool  # TF 2:3: is this a "handling" at all
    is_forvarad: bool  # TF 2:6-7: held/stored by the authority
    is_inkommen_or_upprattad: bool  # TF 2:9-10: received or drawn up
    is_excluded_draft_or_memo: bool  # TF 2:12-14
    has_statutory_secrecy_basis: bool  # TF 2:2: secrecy needs an explicit legal basis


def classify_document(candidate: DocumentCandidate) -> DocumentGateStatus:
    """Loop D: run a candidate through the TF 2:3-2:19 disclosure pipeline.

    This never silently drops a candidate: every input maps to exactly one
    named gate status, in the order the gates actually apply.
    """
    if not candidate.is_handling:
        return DocumentGateStatus.NOT_A_DOCUMENT
    if candidate.is_excluded_draft_or_memo:
        return DocumentGateStatus.EXCLUDED
    if not (candidate.is_forvarad and candidate.is_inkommen_or_upprattad):
        return DocumentGateStatus.NOT_PUBLIC
    if candidate.has_statutory_secrecy_basis:
        return DocumentGateStatus.SECRET
    return DocumentGateStatus.DISCLOSABLE


# Loop C boundary gates, encoded as data (paragraph -> function), matching
# the "paragraferna som funktioner" table in the spec. This is descriptive
# metadata, not an executable legal engine.
TF_CHAPTER_1_GATES: dict[str, str] = {
    "TF 1:1": "PURPOSE: fritt meningsutbyte, allsidig upplysning, publicering, efterhandsansvar",
    "TF 1:7": "ACQUIRE/TX: anskaffa och meddela information",
    "TF 1:8": "PRE-BLOCK: stoppar offentlig forhandsgranskning och vissa hindrande atgarder",
    "TF 1:9": "EXCLUSIVE: ingrepp/ansvar kraver stod i TF",
    "TF 1:10": "INTERPRET: tillampningsport, hellre fria an falla i tveksamma fall",
}

TF_CHAPTER_2_GATES: dict[str, str] = {
    "TF 2:1": "OBSERVE: ratt att ta del av allmanna handlingar",
    "TF 2:2": "EXCEPTION: sekretess bara inom specificerade intressekategorier, med lagstod",
    "TF 2:3": "TYPE: ar objektet en handling?",
    "TF 2:4": "PUBLIC?: forvarad + inkommen/upprattad = allman",
    "TF 2:6_2:7": "STORED: nar digital information anses forvarad",
    "TF 2:9": "INPUT: nar handling blir inkommen",
    "TF 2:10": "COMMIT: nar handling blir upprattad",
    "TF 2:12_2:14": "EXCLUDE: minnesanteckningar, utkast m.m. halls utanfor",
    "TF 2:15": "READ: tillhandahallande genast eller sa snart mojligt",
    "TF 2:16": "COPY: kopia/avskrift och skyndsamhetskrav",
    "TF 2:17": "ROUTE: begaran gar till forvarande myndighet",
    "TF 2:18": "IDENTITY_FIREWALL: begransar efterforskning av identitet och syfte",
    "TF 2:19": "APPEAL: avslag/forbehall kan foras vidare till domstol",
}
