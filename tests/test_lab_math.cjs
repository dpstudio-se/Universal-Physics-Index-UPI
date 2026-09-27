// verification_type: software_test; no physical verification is claimed.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {calculate} = require('../src/upi/contribute/static/lab-math.js');
const initial = {frequency: 377, g27: 1, volume: 1, lambda27: 0, curvature: 0, errors: 3};

test('377 Hz reference and forward/inverse closure across the supported domain', () => {
  const reference = calculate(initial);
  assert.ok(Math.abs(reference.bridge.energy_J / 2.49802844655e-31 - 1) < 1e-14);
  assert.ok(Math.abs(reference.bridge.energy_equivalent_mass_kg / 2.779431491077391e-48 - 1) < 1e-14);
  for (const frequency of [1e-100, 8, 377, 1e20, 1e100]) {
    const r = calculate({...initial, frequency});
    assert.ok(r.bridge.relative_error < 1e-12);
    assert.ok(r.bridge.energy_equivalent_mass_kg > 0);
  }
});
test('invalid inputs cannot produce plausible reports', () => {
  for (const field of ['frequency', 'g27', 'volume', 'lambda27', 'curvature']) {
    for (const value of [NaN, Infinity, -Infinity, 1e101, '1', null]) {
      assert.throws(() => calculate({...initial, [field]: value}), RangeError);
    }
  }
  for (const field of ['frequency', 'g27', 'volume']) {
    for (const value of [0, -1, 1e-101]) assert.throws(() => calculate({...initial, [field]: value}));
  }
  for (const errors of [-1, 25, 1.5, NaN]) assert.throws(() => calculate({...initial, errors}));
});
test('compactification controls, curvature sign and independent inverse', () => {
  const r = calculate({...initial, g27: 12, volume: 3, lambda27: 2, curvature: 6});
  assert.equal(r.geometry.g4_L2, 4);
  assert.equal(r.geometry.lambda4_inverse_L2, -1);
  assert.equal(r.geometry.g4_L2 * r.inputs.volume, r.inputs.g27);
  assert.equal(calculate(initial).geometry.lambda4_inverse_L2, 0);
  assert.equal(calculate({...initial, curvature: -6}).geometry.lambda4_inverse_L2, 3);
});
test('Golay correction bound and export retain evidence boundaries', () => {
  for (let errors = 0; errors <= 24; errors++) {
    const r = JSON.parse(JSON.stringify(calculate({...initial, errors})));
    assert.equal(r.golay.within_guarantee, errors <= 3);
    assert.equal(r.claims_experimental_verification, false);
    assert.equal(r.verification_type, 'software_test');
    assert.ok(r.geometry.stop_reason && r.geometry.next_observation);
    assert.ok(r.golay.stop_reason && r.golay.next_observation);
  }
});
