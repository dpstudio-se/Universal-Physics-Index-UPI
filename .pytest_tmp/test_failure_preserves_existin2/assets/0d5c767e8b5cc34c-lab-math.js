/* Pure calculations shared by the browser and Node verification. */
((root) => {
  'use strict';
  const H = 6.62607015e-34;
  const C = 299792458;
  function bounded(value, name, positive = false) {
    if (typeof value !== 'number' || !Number.isFinite(value) || Math.abs(value) > 1e100 ||
        (positive && value < 1e-100)) {
      throw new RangeError(`${name}: ange ett ändligt tal ${positive ? 'mellan 10⁻¹⁰⁰ och 10¹⁰⁰' : 'mellan −10¹⁰⁰ och 10¹⁰⁰'}.`);
    }
    return value;
  }
  function calculate(p) {
    const frequency = bounded(p.frequency, 'Frekvens', true);
    const g27 = bounded(p.g27, 'G₂₇', true);
    const volume = bounded(p.volume, 'V₂₃', true);
    const lambda27 = bounded(p.lambda27, 'Λ₂₇');
    const curvature = bounded(p.curvature, 'Intern krökning');
    if (!Number.isInteger(p.errors) || p.errors < 0 || p.errors > 24) {
      throw new RangeError('Antalet bitfel måste vara ett heltal mellan 0 och 24.');
    }
    const energy = H * frequency;
    const mass = energy / (C * C);
    const inverse = mass * (C * C) / H;
    return {
      version: '1.0.0', verification_type: 'software_test',
      claims_experimental_verification: false,
      inputs: {frequency, g27, volume, lambda27, curvature, errors: p.errors},
      constants: {h_J_s: H, c_m_s: C},
      bridge: {status: 'DER', energy_J: energy, energy_equivalent_mass_kg: mass,
        inverse_Hz: inverse, relative_error: Math.abs(inverse - frequency) / frequency,
        assumption: 'E = hf for the specified quantum energy; m_E is energy-equivalent mass, not photon rest mass.'},
      geometry: {model_status: 'HYP', calculation_status: 'DER', g4_L2: g27 / volume,
        lambda4_inverse_L2: lambda27 - curvature / 2,
        assumptions: ['hbar = c = 1; common length unit L', 'M27 = M4 x K23',
          'Fixed internal metric; no warp factor', 'No additional vacuum contributions'],
        stop_reason: 'Internal geometry, stabilization and vacuum potential not specified.',
        next_observation: 'Specify K23, its metric and stabilizing potential.'},
      golay: {status: 'DER', minimum_distance: 8, guaranteed_correction_radius: 3,
        within_guarantee: p.errors <= 3, operation: 'Bound visualization, not decoding',
        stop_reason: 'No physical field-to-code mapping, correction dynamics or energy budget.',
        next_observation: 'Define encoding and transition rates with energy exchange.'},
      falsification: ['A relative bridge round-trip error above 1e-12 fails this numerical check.',
        'More than 3 bit errors is outside the guaranteed correction radius.',
        'Schwarzschild x flat T23 remains a singular solution in the zero-potential limit; singularity freedom is not established.']
    };
  }
  const api = {calculate};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.UPILab = api;
})(globalThis);
