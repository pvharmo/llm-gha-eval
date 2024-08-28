use regex::Regex;
use rusqlite::Connection;
use std::{
    fs,
    path::{Path, PathBuf},
};

#[derive(Debug)]
pub struct Prediction {
    pub id: Option<u64>,
    pub run_id: u64,
    pub owner: String,
    pub repository: String,
    pub name: String,
    pub model: String,
    pub description_id: String,
    pub description: String,
    pub response: Option<String>,
    pub workflow: Option<String>,
    pub error_type: Option<String>,
    pub error_text: Option<String>,
}

#[derive(Debug)]
pub struct Workflow {
    pub owner: String,
    pub repository: String,
    pub workflow_file: String,
    pub directory: PathBuf,
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

pub fn get_descriptions(workflow: &Workflow) -> Result<Vec<(&str, String)>, std::io::Error> {
    let workflow_level_infos = read_desciption_file(
        &workflow.directory,
        "workflow_level_infos",
        &workflow.workflow_file,
    )?;
    let event_triggers = read_desciption_file(
        &workflow.directory,
        "event_triggers",
        &workflow.workflow_file,
    )?;
    let job_ids = read_desciption_file(&workflow.directory, "job_ids", &workflow.workflow_file)?;
    let job_level_infos = read_desciption_file(
        &workflow.directory,
        "job_level_infos",
        &workflow.workflow_file,
    )?;
    let step_names =
        read_desciption_file(&workflow.directory, "step_names", &workflow.workflow_file)?;
    let step_level_infos = read_desciption_file(
        &workflow.directory,
        "step_level_infos",
        &workflow.workflow_file,
    )?;
    // let dependencies =
    //     read_desciption_file(&workflow.directory, "dependencies", &workflow.workflow_file)?;

    let descriptions = vec![
        // (
        //     "p1",
        //     workflow_level_infos.clone() + event_triggers.as_str() + job_ids.as_str(),
        // ),
        (
            "p2",
            workflow_level_infos.clone()
                + event_triggers.as_str()
                + job_ids.as_str()
                + step_names.as_str(),
        ),
        // (
        //     "p3",
        //     workflow_level_infos.clone()
        //         + event_triggers.as_str()
        //         + job_ids.as_str()
        //         + step_names.as_str()
        //         + dependencies.as_str(),
        // ),
        // (
        //     "p4",
        //     workflow_level_infos.clone()
        //         + event_triggers.as_str()
        //         + job_level_infos.as_str()
        //         + step_names.as_str(),
        // ),
        (
            "p5",
            workflow_level_infos
                + event_triggers.as_str()
                + job_level_infos.as_str()
                + step_level_infos.as_str(),
        ),
    ];

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

pub fn get_repositories() -> Vec<Workflow> {
    let mut repositories = vec![];

    let repository_directories =
        std::env::var("repository_directories").expect("repository_directories is not set");

    let owner_paths = fs::read_dir(repository_directories.clone()).unwrap();
    for owner_path in owner_paths {
        let owner_dir = owner_path.unwrap();
        let owner_name = owner_dir.file_name().to_str().unwrap().to_string();
        let repo_paths = fs::read_dir(owner_dir.path()).unwrap();
        for repo_path in repo_paths {
            let repo_dir = repo_path.unwrap();
            let repo_name = repo_dir.file_name().to_str().unwrap().to_string();
            if let Ok(descriptions_paths) = fs::read_dir(repo_dir.path().join("workflows")) {
                for description_path in descriptions_paths {
                    let description_dir = description_path.unwrap();
                    let description_name =
                        description_dir.file_name().to_str().unwrap().to_string();
                    if repo_dir
                        .path()
                        .join(
                            "generated_descriptions/job_ids_".to_string()
                                + description_name.as_str()
                                + ".txt",
                        )
                        .exists()
                    {
                        let repository = Workflow {
                            owner: owner_name.clone(),
                            repository: repo_name.clone(),
                            workflow_file: description_name.clone(),
                            directory: (repository_directories.clone()
                                + "/"
                                + owner_name.as_str()
                                + "/"
                                + repo_name.as_str())
                            .into(),
                        };
                        repositories.push(repository);
                    }
                }
            }
        }
    }
    repositories
}

pub fn save_inference(prediction: Prediction) {
    let conn = Connection::open("../results/gha_llm_benchmark.db").unwrap();
    let mut stmt = conn.prepare("INSERT INTO predictions (run_id, owner, repository, name, model, description_id, description, response, workflow, error_type, error_text) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)").unwrap();

    stmt.execute((
        &prediction.run_id,
        &prediction.owner,
        &prediction.repository,
        &prediction.name,
        &prediction.model,
        &prediction.description_id,
        &prediction.description,
        &prediction.response,
        &prediction.workflow,
        &prediction.error_type,
        &prediction.error_text,
    ))
    .unwrap();
}
