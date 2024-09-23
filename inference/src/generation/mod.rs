use indicatif::{ProgressBar, ProgressStyle};
use rayon::prelude::*;
use rusqlite::Connection;
use std::time::SystemTime;

// mod docs;
pub mod utils;
pub mod algorithms;
use utils::{get_descriptions, get_repositories, save_inference, Prediction};
use algorithms::{Algorithm, SimpleDeepSeek};

pub fn run() -> u64 {
    let algorithm: Box<dyn Algorithm> = Box::new(SimpleDeepSeek {});
    process(algorithm)
}

fn process(algorithm: Box<dyn Algorithm>) -> u64 {
    let workflows = get_repositories();
    // let v = get_repositories();
    // let workflows: Vec<_> = v.iter().take(1).collect();

    println!("Number of workflows evaluated: {}", workflows.len());

    let pb = ProgressBar::new(workflows.len() as u64);
    pb.set_style(
        ProgressStyle::default_bar()
            .template("{msg} [{wide_bar:.cyan/blue}] {pos}/{len} ({eta})")
            .expect("Invalid progress bar template"),
    );

    let run_id: u64;
    {
        let conn = Connection::open("../results/gha_llm_benchmark.db").unwrap();
        let now = SystemTime::now();
        let unix_time = now
            .duration_since(SystemTime::UNIX_EPOCH)
            .expect("Failed to get Unix time")
            .as_secs();

        conn.execute(
            "INSERT INTO runs (started_at, algorithm) VALUES (?, ?)",
            (unix_time, algorithm.name()),
        )
        .unwrap();
        run_id = conn
            .query_row("SELECT last_insert_rowid()", [], |row| row.get(0))
            .unwrap();
    }

    println!("run_id: {}", run_id);

    workflows.par_iter().for_each(|workflow| {
        let descriptions = get_descriptions(workflow).unwrap();
        for (prompt_id, prompt) in descriptions {
            let (answer, generated_workflow) = algorithm.run(&prompt);
            save_inference(Prediction {
                id: None,
                run_id,
                dataset_id: workflow.id.clone(),
                algorithm: algorithm.name(),
                description_id: prompt_id.to_string(),
                description: prompt.to_string(),
                response: answer,
                workflow: generated_workflow,
                error_type: None,
                error_text: None,
            });
        }
        pb.inc(1);
    });

    println!("done run_id {}", run_id);

    run_id
}