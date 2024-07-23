use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Message {
    role: String,
    content: String,
}

pub struct Assistant {
    temperature: f64,
    model: String,
    description: String,
    top_p: f64,
    api_key: String,
    base_url: String,
    messages: Vec<Message>,
}

impl Assistant {
    pub fn new(model: &str, system_prompt: &str, temperature: f64) -> Assistant {
        Assistant {
            temperature,
            model: model.to_string(),
            description: system_prompt.to_string(),
            top_p: 1.,
            api_key: std::env::var("api_key").expect("API key not found"),
            base_url: std::env::var("base_url").expect("Base URL not found"),
            messages: vec![],
        }
    }
    pub fn run(&mut self, question: &str) -> Result<String, reqwest::Error> {
        self.messages.push(Message {
            role: "user".to_string(),
            content: question.to_string(),
        });

        let mut messages = vec![
            Message {
                role: "system".to_string(),
                content: self.description.to_string(),
            },
        ];
        for message in self.messages.iter() {
            messages.push(message.clone());
        }

        let client = reqwest::blocking::Client::new();

        let data = serde_json::json!({
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": 8192,
            "messages": messages,
        });

        // println!("{:?}", messages);
        let res = client
               .post(self.base_url.to_string() + "/chat/completions")
               .header("Authorization", "Bearer ".to_string() + &self.api_key)
               .header("Content-Type", "application/json")
               .json(&data)
               .send()?;


        let body: serde_json::Value = res.json()?;
        // println!("{:?}", body);

        let answer = body["choices"][0]["message"]["content"].as_str().unwrap();

        self.messages.push(Message {
            role: "assistant".to_string(),
            content: answer.to_string(),
        });

        Ok(answer.to_string())
    }
}
