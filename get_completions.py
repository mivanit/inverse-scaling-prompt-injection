"""getting completions

partially from https://github.com/naimenz/inverse-scaling-eval-pipeline/blob/main/eval_pipeline/openai_api.py"""

from dataclasses import asdict, dataclass
import json
import os
import sys
import typing
import requests
from datetime import timedelta
from typing import Optional, Union


@dataclass
class APIParameters:
	temperature: float = 0.0
	n: int = 1
	max_tokens: int = 5
	top_p: float = 1.0
	logprobs: Optional[int] = 100
	stop: Optional[list[str]] = None
	echo: bool = False


OPENAI_API_KEY: str = open(".openai_key", "r").read().strip()
OPENAI_API_BASE_URL: str = "https://api.openai.com/v1/engines"

def _call_api(
	prompt: Union[str, list[str]],
	model_name: str,
	api_params: Optional[APIParameters] = None,
) -> requests.Response:
	"""This function makes the actual API call, and since we have a rate limit of 60 calls per minute,
	I will add rate limiting here (ideally we could increase the rate limit though)"""
	if api_params is None:
		api_params = APIParameters()
	# OpenAI gave my (Ian's) account the top 100 logprobs,
	# not just the top 5
	data: dict = {
		"prompt": prompt,
		**asdict(api_params),
	}

	headers: dict = {
		"Authorization": f"Bearer {OPENAI_API_KEY}",
		"Content-Type": "application/json",
	}

	url: str = f"{OPENAI_API_BASE_URL}/{model_name}/completions"
	response: requests.Response = requests.post(url, json=data, headers=headers)
	return response


def call_api(
	prompt: Union[str, list[str]],
	model_name: str,
	api_params: Optional[APIParameters] = None,
	max_retries: int = 5,
) -> requests.Response:
	# dodgy error handling and retry code
	count: int = 0
	response_json: dict = {"error": "not an error"}
	while True:
		count += 1
		if count >= max_retries:
			raise ValueError(f"Retried too many times ({max_retries}), got error: {response_json['error']}")
		response = _call_api(prompt, model_name, api_params)
		response_json = response.json()
		if response.status_code != 200:
			print(
				f"Retrying after error {response.status_code}: {response_json['error']}",
				file=sys.stderr,
			)
		else:
			break
	return response

def main(
	prompts_file: str,
	model_names: tuple[str] = ("ada", "babbage", "curie", "davinci"),
	n_prompts: int = 1,
	# n_evals: int = 1,
) -> None:
	# read in prompts
	prompts: list[dict] = list()
	with open(prompts_file, "r") as f:
		for idx, line in enumerate(f):
			if idx >= n_prompts:
				break
			prompts.append(json.loads(line))
			
	output: list = list()
	
	# get completions
	for prompt in prompts:
		temp = {
			"prompt": prompt,
			"completions": dict(),
		}
		for model_name in model_names:
			response = call_api(prompt["prompt"], model_name)
			temp["completions"][model_name] = response.json()["choices"].pop()["text"]
			# ["choices"].pop()["logprobs"]["top_logprobs"].pop()

		output.append(temp)

	# write out completions
	output_str: str = json.dumps(output, indent="\t")
	print(output_str.replace("\t", "    "))
	with open(f"data/completions/completions-{int(hash(json.dumps(prompts)))}.json", "w") as f:
		f.write(output_str)

if __name__ == "__main__":
	import fire
	fire.Fire(main)

