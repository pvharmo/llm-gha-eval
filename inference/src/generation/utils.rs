use regex::Regex;
use rusqlite::Connection;
use std::{
    fs,
    path::{Path, PathBuf},
};
use serde::{Deserialize, Serialize};

#[derive(Debug)]
pub struct Prediction {
    pub id: Option<u64>,
    pub run_id: u64,
    pub dataset_id: String,
    pub algorithm: String,
    pub description_id: String,
    pub description: String,
    pub response: Option<String>,
    pub workflow: Option<String>,
    pub error_type: Option<String>,
    pub error_text: Option<String>,
}

#[derive(Debug)]
pub struct Workflow {
    pub repo_id: u64,
    pub owner: String,
    pub repository: String,
    pub workflow_file: String,
    pub directory: PathBuf,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct WorkflowPrompts {
    pub id: String,
    pub yaml: String,
    pub prompt1: String,
    pub prompt2: String,
    pub prompt3: String,
    pub prompt4: String,
    pub prompt5: String,
    pub prompt1_right: Option<String>,
    pub prompt2_right: Option<String>,
    pub prompt3_right: Option<String>,
    pub prompt4_right: Option<String>,
    pub prompt5_right: Option<String>,
}

pub fn extract_workflow(response: String) -> String {
    if response.contains("```yaml") {
        let re = Regex::new(r"```yaml\s*([\s\S]*?)```").unwrap();
        // let re = Regex::new(r"(?<=```yaml)([\s\S]*?)(?=```)").unwrap();
        re.captures(&response)
            .and_then(|cap| cap.get(1))
            .map(|m| m.as_str().to_string())
            .unwrap_or_else(|| response.to_string())
    } else if response.contains("```") {
        let re = Regex::new(r"```\s*([\s\S]*?)```").unwrap();
        // let re = Regex::new(r"(?<=```)([\s\S]*?)(?=```)").unwrap();
        re.captures(&response)
            .and_then(|cap| cap.get(1))
            .map(|m| m.as_str().to_string())
            .unwrap_or_else(|| response.to_string())
    } else {
        response.to_string()
    }
}

pub fn get_descriptions(workflow: &WorkflowPrompts) -> Result<Vec<(&str, String)>, std::io::Error> {
    let mut descriptions = vec![
        ("prompt1", workflow.prompt1.clone()),
        ("prompt2",workflow.prompt2.clone()),
        ("prompt3",workflow.prompt3.clone()),
        ("prompt4",workflow.prompt4.clone()),
        ("prompt5",workflow.prompt5.clone()),
    ];

    if workflow.prompt1_right.is_some() {
        let prompt1_right = workflow.prompt1_right.clone().unwrap();
        let prompt2_right = workflow.prompt2_right.clone().unwrap();
        let prompt3_right = workflow.prompt3_right.clone().unwrap();
        let prompt4_right = workflow.prompt4_right.clone().unwrap();
        let prompt5_right = workflow.prompt5_right.clone().unwrap();
        let right_descriptions = vec![
            ("prompt1", prompt1_right),
            ("prompt2", prompt2_right),
            ("prompt3", prompt3_right),
            ("prompt4", prompt4_right),
            ("prompt5", prompt5_right),
        ];

        descriptions.extend(right_descriptions);
    }

    Ok(descriptions)
}

pub fn read_desciption_file(
    base_path: &Path,
    description_type: &str,
    workflow_filename: &str,
) -> Result<String, std::io::Error> {
    // println!("{}", workflow_filename);
    let path = base_path.join(
        "generated_descriptions/".to_string() + description_type + "_" + workflow_filename + ".txt",
    );
    // println!("{}", path.display());
    fs::read_to_string(path)
}

pub fn get_repositories() -> Vec<WorkflowPrompts> {
    // read json file
    let rdr = fs::File::open("../dataset/dataset-sm.json").unwrap();
    let json: Result<Vec<WorkflowPrompts>, serde_json::Error> = serde_json::from_reader(rdr);
    json.unwrap()
}

pub fn save_inference(prediction: Prediction) {
    let conn = Connection::open("../results/gha_llm_benchmark.db").unwrap();
    let mut stmt = conn.prepare("INSERT INTO predictions (run_id, dataset_id, algorithm, description_id, description, response, workflow, error_type, error_text) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9)").unwrap();

    stmt.execute((
        &prediction.run_id,
        &prediction.dataset_id,
        &prediction.algorithm,
        &prediction.description_id,
        &prediction.description,
        &prediction.response,
        &prediction.workflow,
        &prediction.error_type,
        &prediction.error_text,
    ))
    .unwrap();
}
