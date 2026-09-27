use std::{env, fs};
use upi_pdf_inspector::{inspect_pdf, to_json_pretty};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let path = env::args().nth(1).ok_or("usage: upi-pdf-inspector <file.pdf>")?;
    let inspection = inspect_pdf(&path)?;
    let json = to_json_pretty(&inspection)?;
    println!("{json}");
    fs::write(format!("{path}.upi.json"), json)?;
    Ok(())
}
