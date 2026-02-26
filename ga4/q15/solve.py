"""
solve.py — ga4/q15: Corrupted JSON streaming parser
Sums metric_968 from valid JSON lines, outputs SHA-256 of the integer sum.
"""
import zipfile
import json
import hashlib

total = 0
valid = 0
invalid = 0

with zipfile.ZipFile("corrupted_logs.zip") as z:
    with z.open("corrupted_logs.json") as f:
        for line in f:
            line = line.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                val = record["context"]["system"]["process"]["metrics"]["metric_968"]
                total += int(val)
                valid += 1
            except Exception:
                invalid += 1

sha = hashlib.sha256(str(total).encode("utf-8")).hexdigest()

with open("answer.txt", "w") as f:
    f.write(f"valid={valid}\n")
    f.write(f"invalid={invalid}\n")
    f.write(f"sum={total}\n")
    f.write(f"sha256={sha}\n")

print(f"Valid records : {valid}")
print(f"Invalid records: {invalid}")
print(f"Sum metric_968 : {total}")
print(f"SHA-256        : {sha}")
