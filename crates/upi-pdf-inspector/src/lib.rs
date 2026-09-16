mod constitutional_scope;
pub use constitutional_scope::{ConstitutionalScope, ScopeStatus};

use lopdf::Document;
use serde::{Deserialize, Serialize};
use std::{collections::HashSet, path::Path};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum InspectError {
    #[error("failed to load PDF: {0}")]
    Load(#[from] lopdf::Error),
    #[error("failed to serialize inspection: {0}")]
    Json(#[from] serde_json::Error),
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum PdfType { TextBased, Scanned, Mixed, Unknown }

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PageText { pub page: u32, pub text: String, pub extractable: bool }

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Evidence { pub page: u32, pub text: String, pub class: EvidenceClass, pub confidence: f32 }

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum EvidenceClass { EST, DER, HYP, SYM, ERR, STOP, Unknown }

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PdfInspection {
    pub file: String,
    pub pages: u32,
    pub pdf_type: PdfType,
    pub confidence: f32,
    pub pages_text: Vec<PageText>,
    pub evidence: Vec<Evidence>,
    pub warnings: Vec<String>,
}

pub fn inspect_pdf<P: AsRef<Path>>(path: P) -> Result<PdfInspection, InspectError> {
    let path_ref = path.as_ref();
    let document = Document::load(path_ref)?;
    let pages_map = document.get_pages();
    let pages = pages_map.len() as u32;
    let mut pages_text = Vec::with_capacity(pages as usize);
    let mut evidence = Vec::new();
    let mut warnings = Vec::new();
    let mut text_pages = HashSet::new();

    for page_number in pages_map.keys().copied().collect::<Vec<_>>() {
        let text = document.extract_text(&[page_number]).unwrap_or_default();
        let extractable = !text.trim().is_empty();
        if extractable { text_pages.insert(page_number); }
        else { warnings.push(format!("page {page_number}: no extractable text")); }
        if extractable {
            evidence.push(Evidence { page: page_number, text: text.clone(), class: classify_evidence(&text), confidence: 0.5 });
        }
        pages_text.push(PageText { page: page_number, text, extractable });
    }

    let ratio = if pages == 0 { 0.0 } else { text_pages.len() as f32 / pages as f32 };
    let pdf_type = match (pages, text_pages.len()) {
        (0, _) => PdfType::Unknown,
        (_, 0) => PdfType::Scanned,
        (p, t) if p == t => PdfType::TextBased,
        _ => PdfType::Mixed,
    };
    Ok(PdfInspection { file: path_ref.display().to_string(), pages, pdf_type, confidence: ratio, pages_text, evidence, warnings })
}

pub fn classify_evidence(text: &str) -> EvidenceClass {
    let lower = text.to_lowercase();
    if lower.contains("error") || lower.contains("incorrect") || lower.contains("invalid") { EvidenceClass::ERR }
    else if lower.contains("we propose") || lower.contains("hypothesis") || lower.contains("conjecture") { EvidenceClass::HYP }
    else if lower.contains("symbolic") || lower.contains("analogy") { EvidenceClass::SYM }
    else if lower.contains("therefore") || lower.contains("derived") || lower.contains("we derive") { EvidenceClass::DER }
    else if lower.contains("established") || lower.contains("measured") || lower.contains("observed") { EvidenceClass::EST }
    else { EvidenceClass::Unknown }
}

pub fn to_json_pretty(inspection: &PdfInspection) -> Result<String, InspectError> { Ok(serde_json::to_string_pretty(inspection)?) }
