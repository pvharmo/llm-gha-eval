use pyo3::prelude::*;
use dotenv::dotenv;

pub mod assistant;
pub mod evaluation;
pub mod generation;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn run_inference() -> PyResult<u64> {
    Ok(generation::run())
}

/// A Python module implemented in Rust.
#[pymodule]
fn inference(m: &Bound<'_, PyModule>) -> PyResult<()> {
    dotenv().ok();
    m.add_function(wrap_pyfunction!(run_inference, m)?)?;
    Ok(())
}
