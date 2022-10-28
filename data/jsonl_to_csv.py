import json
from pathlib import Path

import pandas as pd


def jsonl_to_csv(jsonl_filename, csv_filename=None):
	"""
	Converts a jsonl file to a csv file.
	"""
	if csv_filename is None:
		csv_filename = f"{Path(jsonl_filename).stem}.csv"

	with open(jsonl_filename, "r", encoding="utf-8") as f:
		data = [json.loads(line) for line in f]

	df = pd.DataFrame(data)
	df.to_csv(csv_filename, index=True)

if __name__ == "__main__":
	import fire
	fire.Fire(jsonl_to_csv)