use regex::Regex;
use rusqlite::Connection;

use serde::{Deserialize, Serialize};

use crate::assistant::Assistant;
use crate::generation::utils::Prediction;

pub fn run(prediction: &Prediction, eval_id: u64) {
    let model = "meta-llama/Meta-Llama-3.1-70B-Instruct";
    let system_prompt = "
        You will be given a github actions workflow and you will rate how well it follows the description on a scale from one to five. Give two scores, one for the events and one for the jobs:
        - Give a score of one if the workflow does not follow the description at all.
        - Give a score of two if the workflow has one element that follows the description.
        - Give a score of three if the workflow follows the goal of the description but does not follow any more elements of the description.
        - Give a score of four if the workflow follows the goal of the description and some of the details.
        - Give a score of five if the workflow follows the goal of the description and all of the details.
        Before giving a score, you must explain your reasoning in detail, then, based on your explanation, give a score. Wrap the scores in double parenthesis and prefix the score with event for the evaluation of events and with jobs for the evaluation of jobs.
        Here is an example of how you should format the score: ((event: x)) ((jobs: y)) where x and y are the scores for the events and jobs respectively.
    ";

    let mut assistant = Assistant::new(model, system_prompt, 0.5);

    let mut answer = None;

    if let Some(workflow) = &prediction.workflow {
        let prompt = format!(
            "Here is the description: {} and here is the workflow: {}",
            prediction.description, workflow
        );
        answer = match assistant.run(&prompt) {
            Ok(answer) => Some(answer),
            Err(_) => None,
        };
    }

    let errors: Option<serde_json::Value>;
    let result: Option<serde_json::Value>;

    if let Some(answer) = &answer {
        errors = None;
        result = Some(serde_json::to_value(extract_result(&answer)).unwrap());
    } else {
        errors =
            Some(serde_json::from_str("An error occured while waiting for the answer.").unwrap());
        result = None;
    }

    save_llm_judge(LLMJudgeResult {
        eval_id,
        prediction_id: prediction.id.unwrap(),
        judge_answer: Some("".to_string()),
        result,
        errors,
    });
}

#[derive(Serialize, Deserialize)]
struct JudgeResult {
    event: Option<f64>,
    job: Option<f64>,
}

pub struct LLMJudgeResult {
    eval_id: u64,
    prediction_id: u64,
    judge_answer: Option<String>,
    result: Option<serde_json::Value>,
    errors: Option<serde_json::Value>,
}

fn extract_result(answer: &str) -> JudgeResult {
    let pattern_event = r"\(\(event:\s*(\S+)\)\)";
    let pattern_jobs = r"\(\(jobs:\s*(\S+)\)\)";

    let re_event = Regex::new(pattern_event).unwrap();
    let re_jobs = Regex::new(pattern_jobs).unwrap();

    let events_result = re_event.captures(answer);
    let jobs_result = re_jobs.captures(answer);

    let mut event = None;

    if let Some(captures) = events_result {
        event = Some(captures[1].parse::<f64>().unwrap());
    }

    let mut job = None;

    if let Some(captures) = jobs_result {
        job = Some(captures[1].parse::<f64>().unwrap());
    }

    JudgeResult { event, job }
}

pub fn save_llm_judge(result: LLMJudgeResult) {
    let conn = Connection::open("../results/gha_llm_benchmark.db").unwrap();
    let mut stmt = conn.prepare("INSERT INTO llm_as_a_judge_scores (eval_id, prediction_id, judge_answer, judge_result, errors) VALUES (?1, ?2, ?3, ?4)").unwrap();

    let error = if result.errors.is_some() {
        Some(serde_json::to_string(&result.errors).unwrap())
    } else {
        None
    };
    let judge_result = if result.result.is_some() {
        Some(serde_json::to_string(&result.result).unwrap())
    } else {
        None
    };

    stmt.execute((
        &result.eval_id,
        &result.prediction_id,
        &result.judge_answer,
        judge_result,
        error,
    ))
    .unwrap();
}
