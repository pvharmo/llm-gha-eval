use crate::inference::utils::Prediction;
use rayon::prelude::*;
use rusqlite::Connection;
use std::time::SystemTime;

mod llm_as_judge;

pub fn run(run_id: u64) {
    let (predictions, eval_id) = get_predictions(run_id);

    predictions.par_iter().for_each(|prediction| {
        llm_as_judge::run(&prediction, eval_id);
    });
}

pub fn get_predictions(run_id: u64) -> (Vec<Prediction>, u64) {
    let conn = Connection::open("../results/gha_llm_benchmark.db").unwrap();

    let eval_id: u64;
    {
        let now = SystemTime::now();
        let unix_time = now
            .duration_since(SystemTime::UNIX_EPOCH)
            .expect("Failed to get Unix time")
            .as_secs();

        conn.execute(
            "INSERT INTO evaluations (run_id, started_at) VALUES (?, ?)",
            (run_id, unix_time),
        )
        .unwrap();
        eval_id = conn
            .query_row("SELECT last_insert_rowid()", [], |row| row.get(0))
            .unwrap();
    }

    let mut stmt = conn
        .prepare(
            "
        SELECT run_id, owner, repository, name, model, description_id, description,
                response, workflow, error_type, error_text, id
        FROM predictions
        WHERE run_id = ?1
    ",
        )
        .unwrap();

    let predictions_iter = stmt
        .query_map([run_id], |row| {
            Ok(Prediction {
                id: Some(row.get(11).unwrap()),
                run_id: row.get(0).unwrap(),
                owner: row.get(1).unwrap(),
                repository: row.get(2).unwrap(),
                name: row.get(3).unwrap(),
                model: row.get(4).unwrap(),
                description_id: row.get(5).unwrap(),
                description: row.get(6).unwrap(),
                response: row.get(7).unwrap(),
                workflow: row.get(8).unwrap(),
                error_type: row.get(9).unwrap(),
                error_text: row.get(10).unwrap(),
            })
        })
        .unwrap();

    let mut predictions: Vec<Prediction> = vec![];

    for prediction in predictions_iter {
        predictions.push(prediction.unwrap());
    }

    (predictions, eval_id)
}
