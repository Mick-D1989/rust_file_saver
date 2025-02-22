use pyo3::prelude::*;
use pyo3::types::PyList;
use tokio::fs;
use tokio::task;
use std::path::Path;

/// A helper function to save a single file asynchronously in the specified directory.
async fn save_single_file(directory: &Path, file_name: String, content: Vec<u8>) -> Result<(), String> {
    // Ensure the directory exists
    if !directory.exists() {
        fs::create_dir_all(directory)
            .await
            .map_err(|e| format!("Failed to create directory {}: {}", directory.display(), e))?;
    }

    // Construct the full file path
    let file_path = directory.join(file_name);
    fs::write(&file_path, content)
        .await
        .map_err(|e| format!("Failed to write to {}: {}", file_path.display(), e))
}

/// Save multiple files concurrently in the specified directory.
#[pyfunction]
fn save_files(directory: &str, files: &PyList) -> PyResult<()> {
    let files_vec: Vec<(String, Vec<u8>)> = files
        .iter()
        .map(|item| {
            let tuple = item.downcast::<pyo3::types::PyTuple>().unwrap();
            let file_name: String = tuple.get_item(0).unwrap().extract().unwrap();
            let content: Vec<u8> = tuple.get_item(1).unwrap().extract().unwrap();
            (file_name, content)
        })
        .collect();

    let directory_path = Path::new(directory);

    // Run the asynchronous tasks
    task::block_in_place(|| {
        let runtime = tokio::runtime::Runtime::new().unwrap();
        runtime.block_on(async {
            let tasks: Vec<_> = files_vec
                .into_iter()
                .map(|(file_name, content)| {
                    // Move `file_name` and `content` into the async task
                    save_single_file(directory_path, file_name, content)
                })
                .collect();

            // Wait for all tasks to complete
            let results = futures::future::join_all(tasks).await;

            // Handle potential errors
            for result in results {
                if let Err(err) = result {
                    return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(err));
                }
            }

            Ok(())
        })
    })
}

/// A module containing Rust functionality exposed to Python.
#[pymodule]
fn file_saver_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(save_files, m)?)?;
    Ok(())
}
