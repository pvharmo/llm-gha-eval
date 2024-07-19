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

# cur.execute("DROP TABLE IF EXISTS results")

cur.execute("""
    CREATE TABLE IF NOT EXISTS results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prediction_id INTEGER NOT NULL,
        workflows_comparison JSON,
        actions_comparison JSON,
        deepdiff JSON,
        lint JSON,
        llm_as_a_judge JSON,
        errors JSON,
        FOREIGN KEY(prediction_id) REFERENCES predictions(id)
    )"""
)

