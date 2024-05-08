import json

results = json.loads(open("results/phi3.json").read())

total_success = 0
count = 0
for result in results:
    count += 1
    for test_result in result["test results"]:
        if test_result["valid"] == True:
            total_success += 1
            break

print(total_success / count)
