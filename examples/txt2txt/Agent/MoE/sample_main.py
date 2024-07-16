import logging

# Initialize logging
logger = logging.getLogger(__name__) # avoide using code like logger = get_logger("lambda_invoke_utils")
# Set the logging level
logger.setLevel(logging.DEBUG)
# Create console handler and set level to INFO
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
# Create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# Add formatter to console handler
console_handler.setFormatter(formatter)
# Add console handler to logger
logger.addHandler(console_handler)

from transformers import pipeline

# Decarator to log the input and output of the function, with the function name and the class name
def log_input_output(func):
    def wrapper(*args, **kwargs):
        logger.info(f"Function {func.__name__} received input: {args}")
        output = func(*args, **kwargs)
        logger.info(f"Function {func.__name__} produced output: {output}")
        return output
    return wrapper

@log_input_output
class SentimentAnalysisExpert:
    def __init__(self):
        self.model = pipeline("sentiment-analysis")

    def process(self, input_text):
        return self.model(input_text)

@log_input_output
class TextSummarizationExpert:
    def __init__(self):
        self.model = pipeline("summarization")

    def process(self, input_text):
        return self.model(input_text, max_length=50, min_length=25, do_sample=False)[0]['summary_text']

@log_input_output
class QuestionAnsweringExpert:
    def __init__(self):
        self.model = pipeline("question-answering")

    def process(self, input_text):
        # Assuming the input_text is in the format "question: <question> context: <context>"
        question, context = input_text.split("context:")
        return self.model(question=question, context=context)['answer']

class GatingNetwork:
    def route(self, input_text):
        if "summarize" in input_text:
            return TextSummarizationExpert()
        elif "sentiment" in input_text:
            return SentimentAnalysisExpert()
        elif "question" in input_text:
            return QuestionAnsweringExpert()
        else:
            return None

class MixtureOfExpertsSystem:
    def __init__(self):
        self.gating_network = GatingNetwork()

    def process(self, input_text):
        expert = self.gating_network.route(input_text)
        if expert:
            return expert.process(input_text)
        else:
            return "No suitable expert found"

# Example usage
moe_system = MixtureOfExpertsSystem()
input_text = "Please summarize this text: Transformers (formerly known as pytorch-transformers and pytorch-pretrained-bert) provides general-purpose architectures (BERT, GPT-2, RoBERTa, XLM, DistilBert, XLNet...) for Natural Language Understanding (NLU) and Natural Language Generation (NLG) with over 32+ pretrained models in 100+ languages and deep interoperability between TensorFlow 2.0 and PyTorch."
output = moe_system.process(input_text)
logger.info(f"Output: {output}")
