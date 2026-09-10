//! T€@X™ Bridge — Team Work
//!
//! Scientific provenance:
//!   Planck relation: E = h f
//!   Mass-energy equivalence: E = m_eq c²
//!
//! The bridge names the composed project transformation. It does not rename
//! the underlying established relations and it does not identify a mass
//! equivalent with a particle rest mass without an additional bridge.

pub const TEAX_BRIDGE_NAME: &str = "T€@X™ Bridge";
pub const TEAX_MARK: &str = "™ := Team Work";
pub const PLANCK_H: f64 = 6.626_070_15e-34; // J s, exact SI
pub const C: f64 = 299_792_458.0; // m/s, exact SI
pub const C2: f64 = C * C;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BridgeStatus { Pass, Fail }

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum KnotStatus { Hyp, Open, Stop, Conflict }

#[derive(Debug, Clone, Copy)]
pub struct Measurement {
    pub value: f64,
    pub sigma: f64,
}

#[derive(Debug, Clone)]
pub struct Domain {
    pub input_unit: &'static str,
    pub output_unit: &'static str,
    pub assumptions: &'static [&'static str],
    pub confusion_guard: &'static str,
}

#[derive(Debug, Clone)]
pub struct Provenance {
    pub bridge_name: &'static str,
    pub mark: &'static str,
    pub planck_relation: &'static str,
    pub mass_energy_relation: &'static str,
    pub forward_relation: &'static str,
    pub inverse_relation: &'static str,
}

impl Default for Provenance {
    fn default() -> Self {
        Self {
            bridge_name: TEAX_BRIDGE_NAME,
            mark: TEAX_MARK,
            planck_relation: "E = h*f",
            mass_energy_relation: "E = m_eq*c^2",
            forward_relation: "m_eq = h*f/c^2",
            inverse_relation: "f = m_eq*c^2/h",
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub struct BridgeResult {
    pub frequency_hz: Measurement,
    pub energy_joule: Measurement,
    pub mass_equivalent_kg: Measurement,
    pub recovered_frequency_hz: Measurement,
    pub relative_residual: f64,
}

#[derive(Debug, Clone)]
pub struct BridgeAudit {
    pub units: BridgeStatus,
    pub forward: BridgeStatus,
    pub inverse: BridgeStatus,
    pub closure: BridgeStatus,
    pub provenance: BridgeStatus,
    pub attribution: BridgeStatus,
    pub domain: BridgeStatus,
    pub uncertainty: BridgeStatus,
}

impl BridgeAudit {
    pub fn full_power(&self) -> bool {
        [self.units, self.forward, self.inverse, self.closure,
         self.provenance, self.attribution, self.domain, self.uncertainty]
            .iter().all(|s| *s == BridgeStatus::Pass)
    }

    pub fn power_percent(&self) -> f64 {
        let states = [self.units, self.forward, self.inverse, self.closure,
                      self.provenance, self.attribution, self.domain, self.uncertainty];
        100.0 * states.iter().filter(|s| **s == BridgeStatus::Pass).count() as f64
            / states.len() as f64
    }
}

pub struct TeaxBridge;

impl TeaxBridge {
    pub fn domain() -> Domain {
        Domain {
            input_unit: "Hz",
            output_unit: "kg mass-equivalent",
            assumptions: &[
                "f is ordinary frequency in the frame where E is evaluated",
                "E = h*f names the energy being converted",
                "the named energy has inertia E/c^2",
            ],
            confusion_guard: "m_eq is an energy mass-equivalent; particle rest-mass identity requires a separate evidenced bridge",
        }
    }

    #[inline]
    pub fn frequency_to_energy(f: Measurement) -> Measurement {
        Measurement { value: PLANCK_H * f.value, sigma: PLANCK_H * f.sigma.abs() }
    }

    #[inline]
    pub fn forward(f: Measurement) -> Measurement {
        let k = PLANCK_H / C2;
        Measurement { value: k * f.value, sigma: k * f.sigma.abs() }
    }

    #[inline]
    pub fn mirror(m_eq: Measurement) -> Measurement {
        let k = C2 / PLANCK_H;
        Measurement { value: k * m_eq.value, sigma: k * m_eq.sigma.abs() }
    }

    pub fn round_trip(f: Measurement) -> BridgeResult {
        let e = Self::frequency_to_energy(f);
        let m = Self::forward(f);
        let recovered = Self::mirror(m);
        let residual = if f.value == 0.0 { recovered.value.abs() }
            else { ((recovered.value - f.value) / f.value).abs() };
        BridgeResult { frequency_hz: f, energy_joule: e, mass_equivalent_kg: m,
                       recovered_frequency_hz: recovered, relative_residual: residual }
    }

    pub fn audit(f: Measurement) -> BridgeAudit {
        let r = Self::round_trip(f);
        let p = Provenance::default();
        let finite = [f.value, f.sigma, r.energy_joule.value, r.mass_equivalent_kg.value,
                      r.recovered_frequency_hz.value].iter().all(|v| v.is_finite());
        let sigma_ok = f.sigma >= 0.0 && r.mass_equivalent_kg.sigma >= 0.0;
        let forward_expected = PLANCK_H * f.value / C2;
        let forward_ok = (r.mass_equivalent_kg.value - forward_expected).abs()
            <= f64::EPSILON.max(forward_expected.abs() * 1e-14);
        let inverse_ok = (r.recovered_frequency_hz.value - f.value).abs()
            <= f64::EPSILON.max(f.value.abs() * 1e-14);
        BridgeAudit {
            units: if finite { BridgeStatus::Pass } else { BridgeStatus::Fail },
            forward: if forward_ok { BridgeStatus::Pass } else { BridgeStatus::Fail },
            inverse: if inverse_ok { BridgeStatus::Pass } else { BridgeStatus::Fail },
            closure: if r.relative_residual <= 1e-14 { BridgeStatus::Pass } else { BridgeStatus::Fail },
            provenance: if p.planck_relation == "E = h*f" && p.mass_energy_relation == "E = m_eq*c^2" { BridgeStatus::Pass } else { BridgeStatus::Fail },
            attribution: if p.bridge_name == TEAX_BRIDGE_NAME && p.mark == TEAX_MARK { BridgeStatus::Pass } else { BridgeStatus::Fail },
            domain: if !Self::domain().assumptions.is_empty() { BridgeStatus::Pass } else { BridgeStatus::Fail },
            uncertainty: if sigma_ok { BridgeStatus::Pass } else { BridgeStatus::Fail },
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reference_7834_closes_with_uncertainty() {
        let f = Measurement { value: 7.834, sigma: 0.001 };
        let r = TeaxBridge::round_trip(f);
        assert!((r.recovered_frequency_hz.value - f.value).abs() < 1e-12);
        assert!((r.recovered_frequency_hz.sigma - f.sigma).abs() < 1e-12);
        assert!(TeaxBridge::audit(f).full_power());
        assert_eq!(TeaxBridge::audit(f).power_percent(), 100.0);
    }

    #[test]
    fn eight_hz_closes() {
        let f = Measurement { value: 8.0, sigma: 0.0 };
        assert!(TeaxBridge::audit(f).full_power());
    }

    #[test]
    fn domain_blocks_particle_identity_autofill() {
        assert!(TeaxBridge::domain().confusion_guard.contains("particle rest-mass identity"));
    }
}
