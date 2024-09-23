import inference

from evaluate import evaluate
from aggregate import aggregate

run_id = inference.run_inference() # type: ignore

eval_id = evaluate(run_id)

aggregate(eval_id)