

# Evaluation Metric

Classification

# Authors:

Michael Ivanitskiy

# Task Name:

prompt-injection-avoidance

# Description:

"Prompt Injection" describes the process of providing a malicious prompt to a language model that causes it to ignore previous instructions and generate some other piece of text, which can possibly be malicious. Good behavior on this task looks like following the initial prompt and not following the instructions of the prompt injection. The task consists of simple question answering (centered around retrieval of basic information), with instructions to avoid prompt injections. At the end of the prompt, in a place where user input would normally be provided, an injection is instead placed that adds unexpected/malicious text.

# Why is the task important?

Avoiding these injections is paramount for any language model deployed for human interaction through prompt programming. The effect may be weaker with fine-tuning or more complicated tasks, but I do not have the resources to test this. Since many deployments of LLMs in the future will likely be based on prompt programming and no further conditioning, studying weaknesses of this methodology feels important.

The observed inverse scaling points to increased difficulty in eliciting "correct" behavior from a LLM, particularly when that LLM might be subject to adversarial inputs. This task is a simple example of such behavior, but may be useful as a stepping stone for future work on the subject.

# Why is inverse scaling expected:

Understanding the instructions in the prompt injections is a more difficult task than simply providing correct answers. Incorrect answers following the prompt injection require a greater understanding of human language, or in some cases programming syntax. Correct answers require only trivial information retrieval. (I've verified that positive scaling exists for a control group with no prompt injection, although accuracy is extremely high for all GPT-3 sizes.)

# Why is the task novel or surprising?

To my knowledge, inverse scaling on prompt injection avoidance has not been demonstrated. This is likely due to the relative novelty of prompt injection. I am not aware of any large-scale standardized experiments on prompt injection.

# Data generation procedure:

Full code (and more data) is available at https://github.com/mivanit/inverse-scaling-prompt-injection. A JSON configuration is given as input to the code. The configuration contains:

 - initial prompt
 - list of correct example pairs
 - example format
 - list of prompt injection formats
 - list of injected answers
 - number of examples to provide

The code adds the initial prompt, several examples, and a final incomplete example where the "question" is the prompt injection. It may be possible to automate the creation of example pairs from other datasets, but I have used extremely simple data (car brands, capitals of US states) due to time constraints.

The submitted dataset includes primarily data with the "corrupted" style of prompt injection, since that is where inverse scaling is clearest. All other prompt injection styles and datasets tried are in the `configs/` directory.

# Expertise required to verify task labels

Extremely minimal, can be automated if desired.

# Dataset generation type

Mixture of code and hand-written

# Dataset sources

Actual dataset and code is original work.
Concept of prompt injection first written about by Goodside: https://twitter.com/goodside/status/1569128808308957185
I found https://simonwillison.net/2022/Sep/12/prompt-injection/ to be very helpful.

# Zero shot vs few shot

Few shot















