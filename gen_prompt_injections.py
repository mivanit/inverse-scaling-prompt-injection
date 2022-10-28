"""part of https://github.com/mivanit/inverse-scaling-prompt-injection
by Michael Ivanitskiy
"""

import typing
import json
import random
from pathlib import Path


def mapping_fewshot(
		initial_prompts: list[str],
		example_fmt: str,
		correct_examples: list[tuple[str, str]],
		prompt_injection_formats: list[str],
		injected_answers: list[str],
		n_examples: int = 3,
		n_prompts_gen: int = 10,
		mode: typing.Literal["sequence_prob", "classification"] = "classification", 
	) -> list[dict]:
	"""generate prompt injection tasks
	
	# Parameters:
	 - `initial_prompts : list[str]`   
	   initial (zero shot) prompt, can be blank
	 - `example_fmt : str`
	 	format string for the example. will get keys "ex_Q", "ex_A". {ex_A} should be the **LAST THING IN THE FORMAT STRING**, set it to "" if its the final part of the prompt
	 - `correct_examples : list[tuple[str, str]]`   
	   list of (question, answer) pairs
	 - `prompt_injection_formats : list[str]`   
	   will be formatted with keys "ex_Q", "ex_A", "injected_A"
	 - `injected_answers : list[str]`   
	   list of answers to inject into prompts. code ensures that injected answer is not the same as the correct answer
	 - `n_examples : int`   
	   number of shots. if set to 0, make sure `initial_prompts` is not empty
	   (defaults to `3`)
	 - `n_prompts_gen : int`   
	   number to generate
	   (defaults to `10`)
	
	# Returns:
	 - `list[dict]` 
	   return a list of dicts. dict content depends on depends on `mode`:
	   - `sequence_prob`: keys "prompt", "completion"
	   - `classification`: keys:
	    	"prompt" : str
			"classes" : list[str]
			"answer_index" : int
	"""	
	# prepend " " to all correct examples
	correct_examples = [(f" {q}", f" {a}") for q, a in correct_examples]

	output: list[dict[str, str]] = list()

	for _ in range(n_prompts_gen):

		# Generate a random subset of the examples
		examples_subset: list[tuple[str, str]] = random.sample(correct_examples, n_examples)

		# pick a random prompt injection format
		prompt_inj_fmt: str = random.choice(prompt_injection_formats)

		# pick a final question to ask
		final_example: tuple[str, str] = random.choice(correct_examples)

		# pick a random injected answer
		injected_answer: str = random.choice(injected_answers)

		while injected_answer == final_example[1]:
			# pick a different answer
			injected_answer = random.choice(injected_answers)

		injected_answer = f" {injected_answer}"

		# Generate the prompt, with a random initial prompt
		prompt: list[str] = [random.choice(initial_prompts)]
		for example_Q, example_A in examples_subset:
			prompt.append(example_fmt.format(ex_Q=example_Q, ex_A=example_A))

		# add the injection to the prompt with fake answer
		injected: str = prompt_inj_fmt.format(
			ex_Q=final_example[0], 
			ex_A=final_example[1], 
			injected_A=injected_answer,
		)
		# prompt.append(f"{example_Q_prefix}{injected}\n{example_A_prefix}")
		prompt.append(example_fmt.format(ex_Q=injected, ex_A=""))

		if mode == "sequence_prob":
			output.append(dict(
				prompt = "\n".join(prompt),
				completion = final_example[1],
			))
		elif mode == "classification":
			output.append(dict(
				prompt = "\n".join(prompt),
				classes = [final_example[1], injected_answer],
				answer_index = 0,
			))
		else:
			raise ValueError(f"unknown mode {mode}")


	return output

def count_duplicates(data: list[dict]) -> int:
	"""count the number of duplicate prompts in a list of dicts with key "prompt" """
	prompts: list[str] = [d["prompt"] for d in data]
	return len(prompts) - len(set(prompts))


def mapping_gen_from_file(
		gen_filename: str,
		output_filename: str|None = None,
		**kwargs,
	):
	"""generate prompt injection tasks from a file

	# Parameters:
	 - `gen_filename : str`
	   filename of the json file to generate from, passed to `mapping_fewshot`
	 - `output_filename : str`
	   filename to save to. if `None`, will save to `data/{{Path(gen_filename).stem}}.jsonl`
	   (defaults to `None`)
	 - `**kwargs`
	   passed to `mapping_fewshot`

	kwargs will override any values in the json file, and will be passed to `mapping_fewshot`, whose doctstring is below:

	# mapping_fewshot.__doc__

	"""

	# load generator from file
	generator_params: dict = json.load(open(gen_filename, "r", encoding="utf-8"))

	# augment with kwargs
	generator_params.update(kwargs)
	mode: str = generator_params["mode"]

	# call generator
	data: list[tuple[str, str]] = mapping_fewshot(**generator_params)

	print(f"generated {len(data)} prompts in {mode = } with {count_duplicates(data)} duplicates")

	# store data
	if output_filename is None:
		output_filename = f"data/{Path(gen_filename).stem}-{mode}.jsonl"

	print(f"saving to: '{output_filename}'")

	with open(output_filename, "w", encoding="utf-8") as f:
		for d in data:
			f.write(json.dumps(d) + "\n")


mapping_gen_from_file.__doc__ += mapping_fewshot.__doc__

if __name__ == "__main__":
	import sys
	import fire

	if any(arg in sys.argv for arg in ("-h", "--help", "help")):
		print(mapping_gen_from_file.__doc__)
		sys.exit(0)

	fire.Fire(mapping_gen_from_file)















