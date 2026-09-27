use serde::{Deserialize, Serialize};

/// Constitutional/competence gate for public-sector child-protection actions.
/// This is a provenance model, not a legal conclusion engine.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConstitutionalScope {
    pub instrument: String,
    pub status: ScopeStatus,
    pub rf_refs: Vec<String>,
    pub parental_scope_checked: bool,
    pub state_competence_checked: bool,
    pub tf_ygl_checked: bool,
    pub legal_basis: Option<String>,
    pub notes: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum ScopeStatus {
    InScope,
    OutOfScope,
    StopUnresolved,
}

impl ConstitutionalScope {
    pub fn unresolved(instrument: impl Into<String>) -> Self {
        Self {
            instrument: instrument.into(),
            status: ScopeStatus::StopUnresolved,
            rf_refs: vec![
                "RF 1:1: public power is exercised under the laws".into(),
                "RF 1:2: freedom, dignity, welfare, privacy and family life".into(),
                "RF 1:9: equality, objectivity and impartiality".into(),
            ],
            parental_scope_checked: false,
            state_competence_checked: false,
            tf_ygl_checked: false,
            legal_basis: None,
            notes: vec![
                "No automatic state-power expansion from a child-protection label.".into(),
                "Concrete competence and legal basis must be verified.".into(),
            ],
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn unresolved_scope_fails_closed() {
        let x = ConstitutionalScope::unresolved("EU Kids Act");
        assert_eq!(x.status, ScopeStatus::StopUnresolved);
        assert!(!x.state_competence_checked);
        assert!(!x.parental_scope_checked);
    }
}
