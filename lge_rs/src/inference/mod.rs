use indicatif::{ProgressBar, ProgressStyle};
use rayon::prelude::*;
use rusqlite::Connection;
use std::time::SystemTime;

use crate::assistant::Assistant;

// mod docs;
pub mod utils;
use utils::{extract_workflow, get_descriptions, get_repositories, save_inference, Prediction};

pub fn run() {
    // let workflows = get_repositories();
    let v = get_repositories();
    let workflows: Vec<_> = v.iter().take(100).collect();

    println!("Number of workflows evaluated: {}", workflows.len());

    let pb = ProgressBar::new(workflows.len() as u64);
    pb.set_style(
        ProgressStyle::default_bar()
            .template("{msg} [{wide_bar:.cyan/blue}] {pos}/{len} ({eta})")
            .expect("Invalid progress bar template"),
    );

    let system_prompt =
        "You are a software engineer. Please generate a YAML file based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```.";
    let model = "meta-llama/Meta-Llama-3.1-70B-Instruct".to_string();

    let run_id: u64;
    {
        let conn = Connection::open("../results/gha_llm_benchmark.db").unwrap();
        let now = SystemTime::now();
        let unix_time = now
            .duration_since(SystemTime::UNIX_EPOCH)
            .expect("Failed to get Unix time")
            .as_secs();

        conn.execute(
            "INSERT INTO runs (started_at, models) VALUES (?, ?)",
            (unix_time, &model),
        )
        .unwrap();
        run_id = conn
            .query_row("SELECT last_insert_rowid()", [], |row| row.get(0))
            .unwrap();
    }

    println!("run_id: {}", run_id);

    workflows.par_iter().for_each(|workflow| {
        if let Ok(descriptions) = get_descriptions(workflow) {
            for (description_id, description) in descriptions {
                let mut assistant = Assistant::new(&model, &system_prompt, 0.5);

                let answer = match assistant.run(&description) {
                    Ok(answer) => Some(answer),
                    Err(_) => None,
                };

                let generated_workflow = if answer.is_some() {
                    Some(extract_workflow(answer.clone().unwrap()))
                } else {
                    None
                };

                save_inference(Prediction {
                    id: None,
                    run_id,
                    owner: workflow.owner.clone(),
                    repository: workflow.repository.clone(),
                    name: workflow.workflow_file.clone(),
                    model: model.clone(),
                    description_id: description_id.to_string(),
                    description: description.to_string(),
                    response: answer,
                    workflow: generated_workflow,
                    error_type: None,
                    error_text: None,
                })
            }
        }
        pb.inc(1);
    });

    println!("done run_id {}", run_id)
}
