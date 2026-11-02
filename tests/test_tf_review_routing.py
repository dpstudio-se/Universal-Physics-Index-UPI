import pytest

from upi.tf_review_routing import (
    ActorKind,
    DocumentCandidate,
    DocumentGateStatus,
    ReviewBody,
    assert_jo_jurisdiction,
    classify_document,
    route_review,
)


def test_regering_statsrad_routes_to_ku_not_jo():
    assert route_review(ActorKind.REGERING_STATSRAD) is ReviewBody.KU


def test_myndighet_routes_to_jo():
    assert route_review(ActorKind.MYNDIGHET_DOMSTOL_TJANSTEMAN) is ReviewBody.JO


def test_tf_brott_routes_to_jk():
    assert route_review(ActorKind.TF_BROTT) is ReviewBody.JK


def test_overklagbart_utlamnande_routes_to_domstol():
    assert route_review(ActorKind.OVERKLAGBART_UTLAMNANDE) is ReviewBody.DOMSTOL


def test_odins_eye_mistake_is_guarded_against():
    """ALL PUBLIC ERROR -> JO would be wrong for government/statsrad matters."""
    with pytest.raises(ValueError, match="regering/statsrad is excluded from JO"):
        assert_jo_jurisdiction(ActorKind.REGERING_STATSRAD)
    # myndighet matters are fine under JO
    assert_jo_jurisdiction(ActorKind.MYNDIGHET_DOMSTOL_TJANSTEMAN)


def test_non_document_is_not_a_document():
    candidate = DocumentCandidate(
        is_handling=False,
        is_forvarad=False,
        is_inkommen_or_upprattad=False,
        is_excluded_draft_or_memo=False,
        has_statutory_secrecy_basis=False,
    )
    assert classify_document(candidate) is DocumentGateStatus.NOT_A_DOCUMENT


def test_draft_memo_is_excluded_even_if_stored():
    candidate = DocumentCandidate(
        is_handling=True,
        is_forvarad=True,
        is_inkommen_or_upprattad=True,
        is_excluded_draft_or_memo=True,
        has_statutory_secrecy_basis=False,
    )
    assert classify_document(candidate) is DocumentGateStatus.EXCLUDED


def test_not_stored_or_not_received_is_not_public():
    candidate = DocumentCandidate(
        is_handling=True,
        is_forvarad=False,
        is_inkommen_or_upprattad=True,
        is_excluded_draft_or_memo=False,
        has_statutory_secrecy_basis=False,
    )
    assert classify_document(candidate) is DocumentGateStatus.NOT_PUBLIC


def test_public_document_with_secrecy_basis_is_secret():
    candidate = DocumentCandidate(
        is_handling=True,
        is_forvarad=True,
        is_inkommen_or_upprattad=True,
        is_excluded_draft_or_memo=False,
        has_statutory_secrecy_basis=True,
    )
    assert classify_document(candidate) is DocumentGateStatus.SECRET


def test_public_document_without_secrecy_basis_is_disclosable():
    candidate = DocumentCandidate(
        is_handling=True,
        is_forvarad=True,
        is_inkommen_or_upprattad=True,
        is_excluded_draft_or_memo=False,
        has_statutory_secrecy_basis=False,
    )
    assert classify_document(candidate) is DocumentGateStatus.DISCLOSABLE
