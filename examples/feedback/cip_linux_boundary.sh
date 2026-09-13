#!/bin/sh
# Executable OS permission controls in a NEW temporary Linux installation only.
set -eu
[ "$(id -u)" = 0 ] || { echo 'STOP: privileged fixture provisioner required'; exit 1; }
library=$1
CIP_ROOT=$(mktemp -d /tmp/upi-cip-boundary.XXXXXX)
export CIP_ROOT
chmod 755 "$CIP_ROOT"
mkdir -p "$CIP_ROOT/trusted/history" "$CIP_ROOT/trusted/promotion" \
    "$CIP_ROOT/chambers/a" "$CIP_ROOT/chambers/b"
chmod 755 "$CIP_ROOT/trusted" "$CIP_ROOT/trusted/history" "$CIP_ROOT/trusted/promotion" \
    "$CIP_ROOT/chambers" "$CIP_ROOT/chambers/a" "$CIP_ROOT/chambers/b"
printf '%s\n' '{"status":"HYP","version":"fixture-1"}' > "$CIP_ROOT/trusted/history/accepted"
cp "$library" "$CIP_ROOT/trusted/rules"
printf '%s\n' 'fixture manifest; not canonical UPI' > "$CIP_ROOT/trusted/manifest"
sha256sum "$CIP_ROOT/trusted/rules" | cut -d ' ' -f 1 > "$CIP_ROOT/trusted/trust"
sha256sum "$CIP_ROOT/trusted/history/accepted" | cut -d ' ' -f 1 > "$CIP_ROOT/trusted/checkpoint.sha256"
printf '%s\n' 'BLOCKED' > "$CIP_ROOT/trusted/promotion/state"
cp "$CIP_ROOT/trusted/history/accepted" "$CIP_ROOT/chambers/a/candidate"
cp "$CIP_ROOT/trusted/history/accepted" "$CIP_ROOT/chambers/b/candidate"
chown 41001:41001 "$CIP_ROOT/chambers/a/candidate"
chown 41002:41002 "$CIP_ROOT/chambers/b/candidate"
chmod 644 "$CIP_ROOT/chambers/a/candidate" "$CIP_ROOT/chambers/b/candidate"
chmod 444 "$CIP_ROOT/trusted/manifest" "$CIP_ROOT/trusted/trust" "$CIP_ROOT/trusted/rules" \
    "$CIP_ROOT/trusted/checkpoint.sha256" "$CIP_ROOT/trusted/history/accepted" \
    "$CIP_ROOT/trusted/promotion/state"
. "$CIP_ROOT/trusted/rules"
# Fixture has one root controller. Exclusive lock covers all launches and recovery.
exec 9>"$CIP_ROOT/trusted/broker.lock"
flock -x 9
pass() { printf 'PASS %s\n' "$1"; }
deny_write() {
    label=$1; target=$2
    before=$(sha256sum "$target")
    if cip_writer sh -c 'printf corrupted > "$1"' sh "$target" 2>/dev/null; then
        echo "FAIL $label"; exit 1
    fi
    [ "$(sha256sum "$target")" = "$before" ] || exit 1
    pass "$label"
}
cip_writer sh -c 'printf corrupted > "$1"' sh "$CIP_ROOT/chambers/a/candidate"
pass candidate_write_allowed
deny_write other_chamber "$CIP_ROOT/chambers/b/candidate"
deny_write own_manifest "$CIP_ROOT/trusted/manifest"
deny_write verifier_rules "$CIP_ROOT/trusted/rules"
deny_write trust_configuration "$CIP_ROOT/trusted/trust"
deny_write promotion_state "$CIP_ROOT/trusted/promotion/state"
deny_write checkpoint_replacement "$CIP_ROOT/trusted/history/accepted"
if cip_writer rm "$CIP_ROOT/trusted/history/accepted" 2>/dev/null; then exit 1; fi
pass checkpoint_delete
if cip_writer ln -s "$CIP_ROOT/trusted/manifest" "$CIP_ROOT/chambers/a/escape" 2>/dev/null; then exit 1; fi
pass symlink_escape
if cip_writer chmod 777 "$CIP_ROOT/trusted/rules" 2>/dev/null; then exit 1; fi
pass rules_permission_change
if cip_writer sh -c 'echo escaped > /tmp/upi-cip-escape-$$' 2>/dev/null; then exit 1; fi
pass write_outside_scope
[ "$(cip_writer id -u)" = 41001 ] || exit 1
[ "$(cip_verifier id -u)" = 41003 ] || exit 1
pass distinct_identities
cip_verifier cat "$CIP_ROOT/chambers/a/candidate" >/dev/null
if cip_verifier sh -c 'echo changed > "$1"' sh "$CIP_ROOT/chambers/a/candidate" 2>/dev/null; then exit 1; fi
pass verifier_read_only
before=$(sha256sum "$CIP_ROOT/chambers/a/candidate")
# Trusted fault injection, not an operation available to either restricted identity.
cp "$CIP_ROOT/trusted/history/accepted" "$CIP_ROOT/trusted/saved"
printf invalid > "$CIP_ROOT/trusted/history/accepted"
if cip_recover; then exit 1; fi
[ "$(sha256sum "$CIP_ROOT/chambers/a/candidate")" = "$before" ] || exit 1
pass invalid_checkpoint_no_change
cp "$CIP_ROOT/trusted/saved" "$CIP_ROOT/trusted/history/accepted"
chmod 444 "$CIP_ROOT/trusted/history/accepted"
cip_recover
[ "$(sha256sum "$CIP_ROOT/chambers/a/candidate" | cut -d ' ' -f 1)" = \
  "$(cat "$CIP_ROOT/trusted/checkpoint.sha256")" ] || exit 1
pass validated_atomic_recovery
cip_writer sh -c 'printf ready > "$1"; exec sleep 2' sh "$CIP_ROOT/chambers/a/candidate" &
writer_job=$!
while [ "$(cat "$CIP_ROOT/chambers/a/candidate")" != ready ]; do sleep 0.05; done
if cip_recover; then exit 1; fi
wait "$writer_job"
pass active_writer_recovery_stop
mv "$CIP_ROOT/trusted/history/accepted" "$CIP_ROOT/trusted/history/held"
if cip_recover; then exit 1; fi
mv "$CIP_ROOT/trusted/history/held" "$CIP_ROOT/trusted/history/accepted"
pass missing_checkpoint_stop
cp "$CIP_ROOT/trusted/rules" "$CIP_ROOT/trusted/rules.saved"
printf changed > "$CIP_ROOT/trusted/rules"
if cip_writer true; then exit 1; fi
cp "$CIP_ROOT/trusted/rules.saved" "$CIP_ROOT/trusted/rules"
chmod 444 "$CIP_ROOT/trusted/rules"
pass altered_verifier_stop
chmod 666 "$CIP_ROOT/trusted/manifest"
if cip_writer true; then exit 1; fi
if cip_recover; then exit 1; fi
pass unsafe_permissions_stop
chmod 444 "$CIP_ROOT/trusted/manifest"
printf 'FIXTURE %s\n' "$CIP_ROOT"
printf 'verification_type: software_test\n'
printf 'production_isolation: STOP; promotion: BLOCKED\n'
# Keep the small fixture for inspection. No recursive cleanup or host data changes.
