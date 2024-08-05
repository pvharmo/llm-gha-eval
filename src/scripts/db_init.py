import sqlite3

con = sqlite3.connect("results/gha_llm_benchmark.db")
cur = con.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS runs(
        run_id INTEGER PRIMARY KEY AUTOINCREMENT,
        started_at INTEGER NOT NULL,
        models JSON NOT NULL
    )"""
)

cur.execute("""
    CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        owner TEXT NOT NULL,
        repository TEXT NOT NULL,
        name TEXT NOT NULL,
        model TEXT NOT NULL,
        description_id TEXT,
        description TEXT,
        response TEXT,
        workflow TEXT,
        error_type TEXT,
        error_text TEXT,
        FOREIGN KEY(run_id) REFERENCES runs(run_id)
    )"""
)

# cur.execute("DROP TABLE IF EXISTS llm_as_a_judge")
# cur.execute("DROP TABLE IF EXISTS lint")
# cur.execute("DROP TABLE IF EXISTS evaluations")
# cur.execute("DROP TABLE IF EXISTS deepdiff")
# cur.execute("DROP TABLE IF EXISTS bleu")
# cur.execute("DROP TABLE IF EXISTS actions_comparison")

cur.execute("""
    CREATE TABLE IF NOT EXISTS evaluations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        started_at INTEGER NOT NULL,
        run_id JSON NOT NULL
    )"""
)

cur.execute("""
    CREATE TABLE IF NOT EXISTS lints(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        eval_id INTEGER NOT NULL,
        prediction_id INTEGER NOT NULL,
        lint JSON,
        errors JSON,
        FOREIGN KEY(eval_id) REFERENCES evaluations(id),
        FOREIGN KEY(prediction_id) REFERENCES predictions(id)
    )"""
)

cur.execute("""
    CREATE TABLE IF NOT EXISTS deepdiffs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        eval_id INTEGER NOT NULL,
        prediction_id INTEGER NOT NULL,
        deepdiff JSON,
        errors JSON,
        FOREIGN KEY(eval_id) REFERENCES evaluations(id),
        FOREIGN KEY(prediction_id) REFERENCES predictions(id)
    )"""
)

cur.execute("""
    CREATE TABLE IF NOT EXISTS actions_comparisons(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        eval_id INTEGER NOT NULL,
        prediction_id INTEGER NOT NULL,
        actions_comparison JSON,
        errors JSON,
        FOREIGN KEY(eval_id) REFERENCES evaluations(id),
        FOREIGN KEY(prediction_id) REFERENCES predictions(id)
    )"""
)

cur.execute("""
    CREATE TABLE IF NOT EXISTS bleu_scores(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        eval_id INTEGER NOT NULL,
        prediction_id INTEGER NOT NULL,
        score INTEGER,
        errors JSON,
        FOREIGN KEY(eval_id) REFERENCES evaluations(id),
        FOREIGN KEY(prediction_id) REFERENCES predictions(id)
    )"""
)

cur.execute("""
    CREATE TABLE IF NOT EXISTS llm_as_a_judge_scores(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        eval_id INTEGER NOT NULL,
        prediction_id INTEGER NOT NULL,
        judge_answer TEXT,
        judge_result JSON,
        errors JSON,
        FOREIGN KEY(eval_id) REFERENCES evaluations(id),
        FOREIGN KEY(prediction_id) REFERENCES predictions(id)
    )"""
)
