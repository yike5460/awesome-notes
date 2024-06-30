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

# Define the acceptance grade for a candidate implementation, 1 to 10
acceptance_grade = 7

def generate_candidate_implementations():
    """_summary_
    Generate initial evaluation criteria and grader prompts.

    Returns:
        _type_: _description_
    """    
    candidates = [
        {"function": "def evaluate_output(output): return len(output.split()) > 5", "prompt": "Is the output longer than 5 words?"},
        {"function": "def evaluate_output(output): return 'error' not in output.lower()", "prompt": "Does the output contain the word 'error'?"},
    ]
    return candidates

def collect_user_feedback(candidates, outputs):
    """_summary_
    Present candidate implementations to users and collect their grades for a subset of LLM outputs.

    Args:
        candidates (_type_): _description_
        outputs (_type_): _description_

    Returns:
        _type_: _description_
    """    
    feedback = []
    for candidate in candidates:
        grades = []
        for output in outputs:
            grade = input(f"Evaluate output '{output}' with prompt '{candidate['prompt']}': ")
            grades.append(int(grade))
        feedback.append({"candidate": candidate, "grades": grades})
    return feedback

def refine_implementations(feedback):
    """_summary_
    Use the collected feedback to refine and select the best candidate implementations.

    Args:
        feedback (_type_): _description_

    Returns:
        _type_: _description_
    """    
    refined_candidates = []
    for item in feedback:
        candidate = item["candidate"]
        average_grade = sum(item["grades"]) / len(item["grades"])
        if average_grade > acceptance_grade:  # Assume a grading scale of 1 to 10
            refined_candidates.append(candidate)
    return refined_candidates

def iterative_alignment_process(outputs):
    """_summary_
    Repeat the process of generating, collecting feedback, and refining until satisfactory alignment is achieved.

    Args:
        outputs (_type_): _description_

    Returns:
        _type_: _description_
    """    
    candidates = generate_candidate_implementations()
    logger.info(f"Initial candidate implementations: {candidates}")
    while True:
        feedback = collect_user_feedback(candidates, outputs)
        logger.info(f"Collected feedback: {feedback}")
        refined_candidates = refine_implementations(feedback)
        logger.info(f"Refined candidate implementations: {refined_candidates}")
        if refined_candidates == candidates:
            break
        candidates = refined_candidates
    return candidates

# Example LLM outputs
outputs = ["This is a test output.", "Another example output without error.", "Short output."]

# Run the iterative alignment process
final_candidates = iterative_alignment_process(outputs)
logging.info("Final candidate implementations:", final_candidates)
