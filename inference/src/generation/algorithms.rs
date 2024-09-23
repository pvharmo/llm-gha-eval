use crate::assistant::Assistant;
use super::utils::extract_workflow;

pub trait Algorithm: Sync {
    fn algo_type(&self) -> String;
    fn model_name(&self) -> String;
    fn name(&self) -> String {
        self.algo_type() + "-" + &self.model_name()
    }
    fn run(&self, prompt: &str) -> (Option<String>, Option<String>);
}

pub struct SimpleDeepSeek;
impl Algorithm for SimpleDeepSeek {
    fn model_name(&self) -> String {
        "deepseek-chat".to_string()
    }

    fn algo_type(&self) -> String {
        "Simple".to_string()
    }

    fn run(&self, prompt: &str) -> (Option<String>, Option<String>) {
        let system_prompt =
            "You are an expert devops engineer. Please generate a YAML file based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```.";
        let model = self.model_name();

        let mut assistant = Assistant::new(&model, &system_prompt, 0.5);
        let answer = match assistant.run(&prompt.to_string()) {
            Ok(answer) => Some(answer),
            Err(_) => None,
        };


        let generated_workflow = if answer.is_some() {
            Some(extract_workflow(answer.clone().unwrap()))
        } else {
            None
        };

        (answer, generated_workflow)
    }
}
pub struct SimpleLlama8b;
impl Algorithm for SimpleLlama8b {
    fn model_name(&self) -> String {
        "Llama-3.1-8B".to_string()
    }

    fn algo_type(&self) -> String {
        "Simple".to_string()
    }

    fn run(&self, prompt: &str) -> (Option<String>, Option<String>) {
        let system_prompt =
            "You are an expert devops engineer. Please generate a YAML file based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```.";
        let model = "meta-llama/Meta-Llama-3.1-8B-Instruct".to_string();

        let mut assistant = Assistant::new(&model, &system_prompt, 0.5);
        let answer = match assistant.run(&prompt.to_string()) {
            Ok(answer) => Some(answer),
            Err(_) => None,
        };


        let generated_workflow = if answer.is_some() {
            Some(extract_workflow(answer.clone().unwrap()))
        } else {
            None
        };

        (answer, generated_workflow)
    }
}

pub struct SplitGeneration;
impl Algorithm for SplitGeneration {
    fn model_name(&self) -> String {
        "Llama-3.1-8B".to_string()
    }

    fn algo_type(&self) -> String {
        "WithJudge".to_string()
    }

    fn run(&self, prompt: &str) -> (Option<String>, Option<String>) {
        let mut final_answer = "".to_string();
        let system_prompt =
            "You are an expert devops engineer. Generate a file with Github Actions workflow's events based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```.";
        let model = "meta-llama/Meta-Llama-3.1-8B-Instruct".to_string();

        let mut assistant = Assistant::new(&model, &system_prompt, 0.5);
        let answer = match assistant.run(&prompt.to_string()) {
            Ok(answer) => {
                final_answer.push_str(&answer);
                Some(answer)
            },
            Err(_) => None,
        };

        let generated_events = if answer.is_some() {
            Some(extract_workflow(answer.clone().unwrap()))
        } else {
            None
        };

        let system_prompt =
            "You are an expert devops engineer. Generate a file with Github Actions workflow's jobs and steps based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```.";
        let model = "meta-llama/Meta-Llama-3.1-8B-Instruct".to_string();

        let mut assistant = Assistant::new(&model, &system_prompt, 0.5);
        let answer = match assistant.run(&prompt.to_string()) {
            Ok(answer) => {
                final_answer.push_str(("\n\n---------\n\n".to_string() + &answer).as_str());
                Some(answer)
            },
            Err(_) => None,
        };

        let generated_jobs = if answer.is_some() {
            Some(extract_workflow(answer.clone().unwrap()))
        } else {
            None
        };

        let system_prompt =
            "You are an expert devops engineer. Generate a file with Github Actions workflow's name, permissions, env, concurrency and defaults based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```.";
        let model = "meta-llama/Meta-Llama-3.1-8B-Instruct".to_string();

        let mut assistant = Assistant::new(&model, &system_prompt, 0.5);
        let answer = match assistant.run(&prompt.to_string()) {
            Ok(answer) => {
                final_answer.push_str(("\n\n---------\n\n".to_string() + &answer).as_str());
                Some(answer)
            },
            Err(_) => None,
        };

        let generated_details = if answer.is_some() {
            Some(extract_workflow(answer.clone().unwrap()))
        } else {
            None
        };

        let generated_workflow = if generated_details.is_some() && generated_events.is_some() && generated_jobs.is_some() {
            Some(format!(
                "{}\n{}\n{}",
                generated_details.unwrap(),
                generated_events.unwrap(),
                generated_jobs.unwrap()
            ))
        } else {
            None
        };

        (answer, generated_workflow)
    }
}

pub struct WithJudge;
impl Algorithm for WithJudge {
    fn model_name(&self) -> String {
        "Llama-3.1-8B".to_string()
    }

    fn algo_type(&self) -> String {
        "WithJudge".to_string()
    }

    fn run(&self, prompt: &str) -> (Option<String>, Option<String>) {
        let system_prompt =
            "You are an expert devops engineer. Please generate a YAML file based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```.";
        let model = "meta-llama/Meta-Llama-3.1-8B-Instruct".to_string();

        let mut assistant = Assistant::new(&model, &system_prompt, 0.5);
        let workflow_answer = match assistant.run(&prompt.to_string()) {
            Ok(answer) => answer,
            Err(_) => return (None, None),
        };
        
        let judge_system_prompt = "You are an expert devops engineer. Judge the generated YAML file based on the user's input below.";

        let mut judge_assistant = Assistant::new(&model, &judge_system_prompt, 0.5);
        let judge_answer = match judge_assistant.run(("Here is the user's prompt: ".to_string() + &prompt + "\nand here is the generated workflow"+ &workflow_answer).as_str()) {
            Ok(answer) => answer,
            Err(_) => return (None, None),
        };

        let updater_system_prompt = "You are an expert devops engineer. Update the workflow based on the provided feedback and the prompt given by the user. The output format should be ```yaml <Workflow>```.";
        let mut update_assistant = Assistant::new(&model, &updater_system_prompt, 0.5);

        let answer = match update_assistant.run((
            "Here is the prompt: \n".to_string() + &prompt
            + "\nHere is the workflow: \n" + &workflow_answer
            + "\nHere is the feedback: \n" + &judge_answer
        ).as_str()) {
            Ok(answer) => answer,
            Err(_) => return (None, None),
        };

        let generated_workflow = extract_workflow(answer.clone());
        let answers = "-----------\nFirst Workflow\n-----------\n\n".to_string() + &workflow_answer
            + "\n\n-----------\nJudge answer\n----------- \n\n" + &judge_answer
            + "\n\n-----------\nUpdated workflow\n----------- \n\n" + &answer;

        (Some(answers), Some(generated_workflow))
    }
}

pub struct CoT;
impl Algorithm for CoT {
    fn model_name(&self) -> String {
        "Llama-3.1-8B".to_string()
    }

    fn algo_type(&self) -> String {
        "Simple".to_string()
    }

    fn run(&self, prompt: &str) -> (Option<String>, Option<String>) {
        let system_prompt =
            "You are an expert devops engineer.".to_string()
            + " Please generate a YAML file based on the user's input below."
            + " Todo so, first, anlayze the events required for the workflow."
            + " Then make a list of each job and its steps."
            + " Finally, go through each job and staeps and add the workflow's name, permissions, env, concurrency and defaults."
            + " No additional explanation is needed. The output format for the workflow should be ```yaml <Workflow>```.";
        let model = "meta-llama/Meta-Llama-3.1-8B-Instruct".to_string();

        let mut assistant = Assistant::new(&model, &system_prompt, 0.5);
        let answer = match assistant.run(&prompt.to_string()) {
            Ok(answer) => Some(answer),
            Err(_) => None,
        };


        let generated_workflow = if answer.is_some() {
            Some(extract_workflow(answer.clone().unwrap()))
        } else {
            None
        };

        (answer, generated_workflow)
    }
}