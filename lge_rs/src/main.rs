use rusqlite::Connection;
use dotenv::dotenv;
use rayon::prelude::*;
use indicatif::{ProgressBar, ProgressStyle};
use std::time::SystemTime;

mod assistant;
mod utils;

use utils::{Prediction, extract_workflow, get_descriptions, save_result};

fn main() {
    // rayon::ThreadPoolBuilder::new().num_threads(16).build_global().unwrap();
    dotenv().ok();

    // let workflows = get_repositories();
    let v = utils::get_repositories();
    let workflows: Vec<_> = v.iter().take(1000).collect();

    println!("{}", workflows.len());

    let pb = ProgressBar::new(workflows.len() as u64);
    pb.set_style(ProgressStyle::default_bar()
           .template("{msg} [{wide_bar:.cyan/blue}] {pos}/{len} ({eta})")
           .expect("Invalid progress bar template"));

    let system_prompt = "You are a software engineer. Please generate a YAML file based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```.";
    let model = "pvharmo/codellama-7b-Instruct".to_string();

    let run_id: u64;
    {
        let conn = Connection::open("../results/gha_llm_benchmark.db").unwrap();
        let now = SystemTime::now();
        let unix_time = now.duration_since(SystemTime::UNIX_EPOCH).expect("Failed to get Unix time").as_secs();

        conn.execute("INSERT INTO runs (started_at, models) VALUES (?, ?)", (unix_time, &model)).unwrap();
        run_id = conn.query_row("SELECT last_insert_rowid()", [], |row| row.get(0)).unwrap();
    }

    println!("run_id: {}", run_id);

    workflows.par_iter().for_each(|workflow| {
        if let Ok(descriptions) = get_descriptions(workflow) {
            for (description_id, description) in descriptions {
                let mut assistant = assistant::Assistant::new(
                    &model,
                    system_prompt,
                    0.5,
                );

                let answer = match assistant.run(&description) {
                    Ok(answer) => Some(answer),
                    Err(_) => { None }
                };

                let generated_workflow = if answer.is_some() { Some(extract_workflow(answer.clone().unwrap())) } else { None };

                save_result(Prediction {
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
