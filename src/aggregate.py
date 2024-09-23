import sys

import sqlite3
import json
import pandas as pd


def aggregate(eval_id):
    con = sqlite3.connect("../results/gha_llm_benchmark.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    print("EVAL ID", eval_id)

    cur.execute("""
    SELECT
        p.description_id,
        AVG(CAST(score AS FLOAT)) AS avg_bleu_score,
        COUNT(*) AS row_count
    FROM
        predictions p
    JOIN
        bleu_scores r ON p.id = r.prediction_id
    WHERE
        p.description_id IS NOT NULL
        and r.eval_id = ?
        AND score IS NOT NULL
    GROUP BY
        p.description_id
    """, (eval_id,))
    bleu_score = cur.fetchall()
    print("BLEU SCORE")
    for i in bleu_score:
        print(i[0], i[1])

    # cur.execute("""
    # SELECT
    #     p.description_id,
    #     AVG(CAST(score AS FLOAT)) AS avg_deepdiff_score,
    #     COUNT(*) AS row_count
    # FROM
    #     predictions p
    # JOIN
    #     deepdiffs r ON p.id = r.prediction_id
    # WHERE
    #     p.description_id IS NOT NULL
    #     and r.eval_id = ?
    #     AND score IS NOT NULL
    # GROUP BY
    #     p.description_id
    # """, (eval_id,))
    # deepdiff_score = cur.fetchall()
    # print("DeepDiff Score")
    # for i in deepdiff_score:
    #     print(i[0], i[1])

    # cur.execute("""
    # WITH total AS (
    #     SELECT
    #         p.description_id,
    #         COUNT(*) AS row_count
    #     FROM
    #         predictions p
    #     JOIN
    #         lints r ON p.id = r.prediction_id
    # where r.eval_id = ?
    #     GROUP BY description_id
    # ),
    # filtered_predictions AS (
    #     SELECT
    #         p.description_id,
    #         COUNT(*) AS row_count
    #     FROM
    #         predictions p
    #     JOIN
    #         lints r ON p.id = r.prediction_id
    #     WHERE
    #         r.eval_id = ? AND
    #         NOT EXISTS (
    #             SELECT 1
    #             FROM JSON_EACH(JSON_EXTRACT(lint, '$.output'))
    #             WHERE JSON_EXTRACT(value, '$.kind') = 'syntax-check'
    #         )
    #     GROUP BY
    #         p.description_id
    # )
    # SELECT
    #     fp.description_id,
    #     fp.row_count,
    #     t.row_count,
    #     (fp.row_count * 1.0) / (t.row_count * 1.0) AS ratio
    # FROM
    #     filtered_predictions fp
    # JOIN
    #     total t ON fp.description_id = t.description_id;
    # """, (eval_id,eval_id))
    # accuracy_without_versions_validation = cur.fetchall()
    # print("ACCURACY WITHOUT VERSIONS VALIDATION")
    # for i in accuracy_without_versions_validation:
    #     print(i[0], i[1]/999)

    # cur.execute("""
    # WITH total AS (
    #     SELECT
    #         p.description_id,
    #         COUNT(*) AS row_count
    #     FROM
    #         predictions p
    #     JOIN
    #         lints r ON p.id = r.prediction_id
    # where r.eval_id = ?
    #     GROUP BY description_id
    # ),
    # filtered_predictions AS (
    #     SELECT
    #         p.description_id,
    #         COUNT(*) AS row_count
    #     FROM
    #         predictions p
    #     JOIN
    #         lints r ON p.id = r.prediction_id
    #     WHERE
    #         r.eval_id = ? AND
    #         JSON_EXTRACT(lint, '$.valid') = 1
    #     GROUP BY
    #         p.description_id
    # )
    # SELECT
    #     fp.description_id,
    #     (fp.row_count * 1.0) / (t.row_count * 1.0) AS ratio
    # FROM
    #     filtered_predictions fp
    # JOIN
    #     total t ON fp.description_id = t.description_id;
    # """, (eval_id,eval_id))
    # accuracy_with_versions_validation = cur.fetchall()
    # print("ACCURACY WITH VERSIONS VALIDATION")
    # for i in accuracy_with_versions_validation:
    #     print(i[0], i[1])

    cur.execute("""
    SELECT
        p.workflow, r.lint, b.score, p.description, p.description_id
    FROM
        predictions p
    JOIN
        lints r ON p.id = r.prediction_id
    JOIN
        bleu_scores b ON p.id = b.prediction_id
    WHERE
        p.description_id IS NOT NULL
        AND r.eval_id = ?
        AND b.eval_id = ?
        AND b.score IS NOT NULL
    """, (eval_id,eval_id))
    results = cur.fetchall()

    kind = []

    validity = {
        "prompt1": {
            "valid": 0,
            "total": 0
        },
        "prompt2": {
            "valid": 0,
            "total": 0
        },
        "prompt3": {
            "valid": 0,
            "total": 0
        },
        "prompt4": {
            "valid": 0,
            "total": 0
        },
        "prompt5": {
            "valid": 0,
            "total": 0
        },
    }

    for result in results:
        lint = json.loads(result["lint"])
        valid = True
        if lint is None or len(lint) == 0:
            continue
        for lint_output in lint["output"]:
            kind.append(lint_output["kind"])
            if lint_output["kind"] == "syntax-check" and "ail-fast" not in lint_output["message"]:
                valid = False
        validity[result["description_id"]]["total"] += 1
        if valid:
            validity[result["description_id"]]["valid"] += 1

    print("Lint validation")
    for key in validity.keys():
        if validity[key]["total"] == 0:
            print(key, "division by 0")
        else:
            print(key, validity[key]["valid"]/validity[key]["total"])
    print("Number of predictions per description")
    for key in validity.keys():
        print(key, validity[key]["total"])

    print("KIND")
    print(pd.DataFrame(kind).value_counts())

if __name__ == "__main__":
    try:
        eval_id = int(sys.argv[1])
    except:
        raise Exception("Please provide a eval_id as an argument")
    aggregate(eval_id)