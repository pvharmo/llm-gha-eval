import sys

import sqlite3
import json
import pandas as pd

try:
    eval_id = int(sys.argv[1])
except:
    print("Please provide a eval_id as an argument")

con = sqlite3.connect("results/gha_llm_benchmark.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

cur.execute("""
SELECT 
    p.description_id,
    AVG(CAST(JSON_EXTRACT(r.workflows_comparison, '$.bleu_score') AS FLOAT)) AS avg_bleu_score,
    COUNT(*) AS row_count
FROM 
    predictions p
JOIN 
    results r ON p.id = r.prediction_id
WHERE 
    p.description_id IS NOT NULL
    and r.eval_id = ?
    AND JSON_VALID(r.workflows_comparison)
    AND JSON_EXTRACT(r.workflows_comparison, '$.bleu_score') IS NOT NULL
GROUP BY 
    p.description_id
""", (eval_id,))
bleu_score = cur.fetchall()
print("BLEU SCORE")
for i in bleu_score:
    print(i[0], i[1])

cur.execute("""
WITH total AS (
    SELECT 
        p.description_id,
        COUNT(*) AS row_count
    FROM 
        predictions p
    JOIN 
        results r ON p.id = r.prediction_id
  where r.eval_id = ?
    GROUP BY description_id
),
filtered_predictions AS (
    SELECT 
        p.description_id,
        COUNT(*) AS row_count
    FROM 
        predictions p
    JOIN 
        results r ON p.id = r.prediction_id
    WHERE 
        r.eval_id = ? AND
        NOT EXISTS (
            SELECT 1
            FROM JSON_EACH(JSON_EXTRACT(lint, '$[0].output'))
            WHERE JSON_EXTRACT(value, '$.kind') = 'syntax-check'
        )
    GROUP BY 
        p.description_id
)
SELECT 
    fp.description_id,
    fp.row_count,
    t.row_count,
    (fp.row_count * 1.0) / (t.row_count * 1.0) AS ratio
FROM 
    filtered_predictions fp
JOIN 
    total t ON fp.description_id = t.description_id;
""", (eval_id,eval_id))
accuracy_without_versions_validation = cur.fetchall()
print("ACCURACY WITHOUT VERSIONS VALIDATION")
for i in accuracy_without_versions_validation:
    print(i[0], i[1]/999)

cur.execute("""
WITH total AS (
    SELECT 
        p.description_id,
        COUNT(*) AS row_count
    FROM 
        predictions p
    JOIN 
        results r ON p.id = r.prediction_id
  where r.eval_id = ?
    GROUP BY description_id
),
filtered_predictions AS (
    SELECT 
        p.description_id,
        COUNT(*) AS row_count
    FROM 
        predictions p
    JOIN 
        results r ON p.id = r.prediction_id
    WHERE 
        r.eval_id = ? AND
        JSON_EXTRACT(lint, '$[0].valid') = 1
    GROUP BY 
        p.description_id
)
SELECT 
    fp.description_id,
    (fp.row_count * 1.0) / (t.row_count * 1.0) AS ratio
FROM 
    filtered_predictions fp
JOIN 
    total t ON fp.description_id = t.description_id;
""", (eval_id,eval_id))
accuracy_with_versions_validation = cur.fetchall()
print("ACCURACY WITH VERSIONS VALIDATION")
for i in accuracy_with_versions_validation:
    print(i[0], i[1])

cur.execute("""
SELECT 
    p.workflow, r.lint, r.workflows_comparison, p.description, p.description_id
FROM 
    predictions p
JOIN 
    results r ON p.id = r.prediction_id
WHERE 
    p.description_id IS NOT NULL
    and r.eval_id = ?
    AND JSON_VALID(r.workflows_comparison)
    AND JSON_EXTRACT(r.workflows_comparison, '$.bleu_score') IS NOT NULL
""", (eval_id,))
results = cur.fetchall()

kind = []

validity = {
    "p1": {
        "valid": 0,
        "invalid": 0
    },
    "p2": {
        "valid": 0,
        "invalid": 0
    },
    "p3": {
        "valid": 0,
        "invalid": 0
    },
    "p4": {
        "valid": 0,
        "invalid": 0
    },
    "p5": {
        "valid": 0,
        "invalid": 0
    },
}

for result in results:
    lint = json.loads(result["lint"])
    valid = True
    if lint is None or len(lint) == 0:
        continue
    for lint_output in lint[0]["output"]:
        kind.append(lint_output["kind"])
        if lint_output["kind"] == "syntax-check" or lint_output["kind"] == "workflow-syntax-check":
            valid = False

print("KIND")
print(pd.DataFrame(kind).value_counts())