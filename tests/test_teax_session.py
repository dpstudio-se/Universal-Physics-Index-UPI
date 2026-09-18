from upi.teax_session import CoreId, CoreSelector, SessionGuard, SessionState, UNSIGNED_SESSION_SECONDS, TEAX_SESSION_SECONDS, TeaxTagVerifier

def test_default_core():
    assert CoreSelector.select(None) is CoreId.TEAX

def test_all_cores():
    for core in CoreId:
        assert CoreSelector.select(core.value) is core

def test_five_min_unsigned():
    s = SessionGuard().start(CoreId.TEAX, now=1000)
    assert s.expires_at - s.issued_at == UNSIGNED_SESSION_SECONDS == 300

def test_thirty_min_verified():
    s = SessionGuard().start(CoreId.TEAX_PLUS, tag_verified=True, now=1000)
    assert s.expires_at - s.issued_at == TEAX_SESSION_SECONDS == 1800

def test_lock_at_expiry():
    g = SessionGuard()
    s = g.start(CoreId.TEAX, now=1000)
    assert g.status(s, now=1299).state is SessionState.ACTIVE
    assert g.status(s, now=1300).state is SessionState.LOCKED

def test_hmac_tag():
    v = TeaxTagVerifier(b"test-secret")
    tag = v.issue("user")
    assert v.verify("user", tag)
    assert not v.verify("other", tag)
    assert not v.verify("user", tag + "x")
