import os
import json
import base64
import boto3
import logging
from botocore.exceptions import ClientError

# Set up logging to output to current stdout for debugging
logger = logging.getLogger()
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

# Initialize the Amazon Bedrock boto3 client
bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name="us-east-1")
# aws bedrock list-foundation-models --region us-east-1 | jq '.modelSummaries[] | {modelId, modelName, providerName}'
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

orignal_template = """
You are given an image containing a workflow diagram. Your task is to:
1. Identify the content of the image and describe the workflow in detail.
2. Extract the objects and their relationships.
3. Transform the extracted workflow into Mermaid chart code.

Here is the image data (in base64 format): {image_data}

Please provide the detailed description first, followed by the Mermaid chart code.
"""

"""
revise the prompt using claude prompt generator: https://github.com/aws-samples/claude-prompt-generator
TODO: 
(1) More example on the mermaid template as few shots for model to choose the optimzed schema according to the description;
(2) PE to obtain the more accurate description for the workflow diagram;
"""
prompt_template = """
<instruction_guide>
# Instruction Guide

## Be clear & direct

Your task is to analyze a workflow diagram in an image and provide a detailed description of the workflow. Additionally, you need to:

1. Extract the objects and their relationships from the image.
2. Transform the extracted workflow into Mermaid chart code.

Follow these steps:

1. Describe the workflow in detail, including all the steps and their relationships, determine which Mermaid chart template (flowchart, sequenceDiagram, timeline, classDiagram, stateDiagram, gantt, erDiagram, xychart-beta) best represents the workflow.
2. Extract the objects (steps, decisions, etc.) and their relationships from the workflow.
3. Use the extracted information to generate the corresponding Mermaid chart code, ensuring generated code strictly follow the Mermaid syntax, e.g. enclosing the node labels in double quotes to ensure that Mermaid correctly interprets the entire label as a single entity, avoiding the parse errors caused by special characters.

Your response should be structured as follows:

<description>
[Detailed description of the workflow and Mermaid chart template selection]
</description>

<mermaid>
[Mermaid chart code representing the workflow]
</mermaid>

## Use examples

Below are examples of workflow diagrams covering all the typical type of mermaid templates, including flowchart, sequenceDiagram, timeline, classDiagram, stateDiagram, gantt, pie and erDiagram. Each example includes a detailed description of the workflow along with Mermaid chart codes. Use these examples as reference when analyzing the workflow diagram in the image.

<example>

<description>
This flow chart represents the process of evaluating and selecting an option based on certain conditions. The workflow begins with the "Start" node, which transitions to a step labeled "Some text." From there, the process continues to the "Continue" node.

After continuing, the process reaches the "Evaluate" decision diamond, which branches out into three possible paths:

If the condition "One" is met, the workflow proceeds to "Option 1."
If the condition "Two" is met, the workflow proceeds to "Option 2."
If the condition "Three" is met, the workflow proceeds to "Option 3."
Each option represents a different outcome based on the evaluation criteria.
</description>

<mermaid>
flowchart LR
    A[Start] --Some text--> B(Continue)
    B --> C{Evaluate}
    C -- One --> D[Option 1]
    C -- Two --> E[Option 2]
    C -- Three --> F[fa:fa-car Option 3]
</mermaid>

<description>
This sequence diagram represents the process of a communication exchange between two individuals, Alice and John. The interaction proceeds as follows:

Alice initiates the conversation by sending a message to John: "Hello John, how are you?"
Alice sends another message to John: "John, can you hear me?"
John responds to Alice with: "Hi Alice, I can hear you!"
John follows up with another message: "I feel great!"
The diagram illustrates a sequence of messages exchanged between Alice and John, highlighting their communication flow.
</description>

<mermaid>
sequenceDiagram
    Alice->>+John: Hello John, how are you?
    Alice->>+John: John, can you hear me?
    John-->>-Alice: Hi Alice, I can hear you!
    John-->>-Alice: I feel great!
</mermaid>

<description>
This timeline diagram represents the process of the Industrial Revolution, detailing its evolution through different phases and technological advancements. The timeline is divided into two main periods: the 17th-20th century and the 21st century.

1. **17th-20th Century**:
   - **Industry 1.0**: Characterized by the use of machinery, water power, and steam power.
   - **Industry 2.0**: Marked by the advent of electricity, internal combustion engines, and mass production techniques.

2. **21st Century**:
   - **Industry 3.0**: Defined by the development and integration of electronics, computers, and automation.
   - **Industry 4.0**: Focuses on the Internet, robotics, and the Internet of Things (IoT).
   - **Industry 5.0**: Encompasses advancements in artificial intelligence, big data, and 3D printing.

The diagram uses vertical dotted lines to connect each industry phase with its corresponding technological innovations, illustrating the progression and transformation of industrial capabilities over time.
</description>

<mermaid>
timeline
    title Timeline of Industrial Revolution
    section 17th-20th century
        Industry 1.0 : Machinery, Water power, Steam <br>power
        Industry 2.0 : Electricity, Internal combustion engine, Mass production
        Industry 3.0 : Electronics, Computers, Automation
    section 21st century
        Industry 4.0 : Internet, Robotics, Internet of Things
        Industry 5.0 : Artificial intelligence, Big data,3D printing
</mermaid>

<description>
This class diagram represents the process of class inheritance in object-oriented programming, specifically illustrating the relationship between a base class "Animal" and its derived classes "Duck," "Fish," and "Zebra." The diagram is structured as follows:

1. **Base Class: Animal**
   - Attributes:
     - `+int age`: An integer representing the age of the animal.
     - `+String gender`: A string representing the gender of the animal.
   - Methods:
     - `+isMammal()`: A method to check if the animal is a mammal.
     - `+mate()`: A method to handle the mating behavior of the animal.

2. **Derived Classes:**
   - **Duck**
     - Attributes:
       - `+String beakColor`: A string representing the color of the duck's beak.
     - Methods:
       - `+swim()`: A method to enable the duck to swim.
       - `+quack()`: A method to enable the duck to quack.
   
   - **Fish**
     - Attributes:
       - `-int sizeInFeet`: An integer representing the size of the fish in feet.
     - Methods:
       - `-canEat()`: A method to determine if the fish can eat.
   
   - **Zebra**
     - Attributes:
       - `+bool is_wild`: A boolean indicating if the zebra is wild.
     - Methods:
       - `+run()`: A method to enable the zebra to run.

The class diagram uses arrows to indicate inheritance, showing that "Duck," "Fish," and "Zebra" inherit from the "Animal" class. Each derived class has its own specific attributes and methods in addition to those inherited from the base class.
</description>

<mermaid>
classDiagram
    Animal <|-- Duck
    Animal <|-- Fish
    Animal <|-- Zebra
    Animal : +int age
    Animal : +String gender
    Animal: +isMammal()
    Animal: +mate()
    class Duck{
      +String beakColor
      +swim()
      +quack()
    }
    class Fish{
      -int sizeInFeet
      -canEat()
    }
    class Zebra{
      +bool is_wild
      +run()
    }
</mermaid>

<description>
This state diagram represents the process of state transitions for an object, such as a vehicle, through different states: Still, Moving, and Crash.

1. **Start State**:
   - The diagram begins with a filled black circle, indicating the initial state.

2. **Still State**:
   - The object starts in the "Still" state.
   - From the "Still" state, the object can transition to the "Moving" state.

3. **Moving State**:
   - Once in the "Moving" state, the object can either:
     - Transition back to the "Still" state.
     - Proceed to the "Crash" state.

4. **Crash State**:
   - In the "Crash" state, the object can transition back to the "Still" state.

5. **End State**:
   - The diagram concludes with a circle containing a smaller filled circle, indicating the final state.

The arrows indicate the possible transitions between these states, illustrating how the object can move from one state to another based on certain conditions or events.
</description>

<mermaid>
stateDiagram
    [*] --> Still
    Still --> [*]
    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
</mermaid>

<description>
This gantt diagram represents the process of task scheduling and progress tracking using a Gantt chart. The chart visually outlines tasks over a specified time period, highlighting their start and end dates as well as their duration.

1. **Sections**:
   - The chart is divided into two main sections: "Section" and "Another."

2. **Tasks in Section**:
   - **A task**: Spans from January 5, 2014, to February 2, 2014.
   - **Task in sec**: Starts on January 12, 2014, and ends on February 2, 2014.

3. **Tasks in Another**:
   - **another task**: Begins on January 5, 2014, and concludes on February 16, 2014.

4. **Timeline**:
   - The timeline at the bottom of the chart marks important dates, such as January 5, 2014, January 12, 2014, January 19, 2014, January 26, 2014, February 2, 2014, February 9, 2014, and February 16, 2014.

The Gantt chart uses horizontal bars to represent the duration of each task, with the length of each bar corresponding to the time span of the task. The interactions between tasks are indicated by their relative positions and overlaps on the timeline, providing a clear visual representation of the project schedule and dependencies.
</description>

<mermaid>
gantt
    title A Gantt Diagram
    dateFormat  YYYY-MM-DD
    section Section
    A task           :a1, 2014-01-01, 30d
    Another task     :after a1  , 20d
    section Another
    Task in sec      :2014-01-12  , 12d
    another task      : 24d
</mermaid>

<description>
This entity relationship diagram represents the process of order management, illustrating the relationships between different entities involved in placing and processing an order. The diagram includes the following components and interactions:

Entities:

CUSTOMER: The individual who places the order.
DELIVERY-ADDRESS: The address where the order will be delivered.
ORDER: The request made by the customer to purchase products.
INVOICE: The bill issued for the order.
PRODUCT-CATEGORY: The classification of products.
PRODUCT: The items that are ordered.
ORDER-ITEM: The specific items included in the order.
Relationships:

CUSTOMER:
Places an order (places).
Has a delivery address (has).
Is liable for the invoice (liable for).
DELIVERY-ADDRESS:
Receives the order (receives).
ORDER:
Includes order items (includes).
Is covered by the invoice (covers).
INVOICE:
Covers the order (covers).
PRODUCT-CATEGORY:
Contains products (contains).
PRODUCT:
Is ordered in order items (ordered in).
ORDER-ITEM:
Is included in the order (includes).
The entity relationship uses arrows to show the direction of relationships and interactions between these entities, providing a clear visual representation of the order management process. Each entity is represented by a green box, and the relationships are labeled with descriptive text to explain the nature of the interaction.
</description>

<mermaid>
erDiagram
    CUSTOMER }|..|{ DELIVERY-ADDRESS : has
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER ||--o{ INVOICE : "liable for"
    DELIVERY-ADDRESS ||--o{ ORDER : receives
    INVOICE ||--|{ ORDER : covers
    ORDER ||--|{ ORDER-ITEM : includes
    PRODUCT-CATEGORY ||--|{ PRODUCT : contains
    PRODUCT ||--o{ ORDER-ITEM : "ordered in"
</mermaid>

<description>
This xy chart represents the process of tracking sales revenue over the course of a year. The chart combines a bar graph and a line graph to illustrate monthly revenue figures.

1. **Title**:
   - "Sales Revenue"

2. **Axes**:
   - **Vertical Axis** (Y-axis): Represents revenue in dollars ($), with increments of 500, ranging from 4000 to 11000.
   - **Horizontal Axis** (X-axis): Represents the months of the year, from January (jan) to December (dec).

3. **Data Representation**:
   - **Bar Graph**: The green bars represent the revenue for each month. The height of each bar corresponds to the revenue amount.
   - **Line Graph**: A red line connects the top of each bar, providing a visual representation of the trend in revenue over the year.

4. **Monthly Revenue**:
   - The revenue starts at around $5000 in January.
   - It increases steadily each month, peaking in July at around $10500.
   - After July, the revenue begins to decline, reaching approximately $4500 in December.

The xy chart clearly shows the seasonal trend in sales revenue, with a significant increase during the middle of the year and a decline towards the end. This visual representation helps in understanding the monthly performance and identifying peak revenue periods.
</description>

<mermaid>
xychart-beta
    title "Sales Revenue"
    x-axis [jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec]
    y-axis "Revenue (in $)" 4000 --> 11000
    bar [5000, 6000, 7500, 8200, 9500, 10500, 11000, 10200, 9200, 8500, 7000, 6000]
    line [5000, 6000, 7500, 8200, 9500, 10500, 11000, 10200, 9200, 8500, 7000, 6000]
</mermaid>

</example>

</instruction_guide>
"""

def encode_image(image_path):
    logger.info(f"Encoding image: {image_path}")
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

def run_multi_modal_prompt(bedrock_runtime, model_id, messages, max_tokens):
    """
    Invokes a model with a multimodal prompt.
    Args:
        bedrock_runtime: The Amazon Bedrock boto3 client.
        model_id (str): The model ID to use.
        messages (JSON): The messages to send to the model.
        max_tokens (int): The maximum number of tokens to generate.
    Returns:
        The response from the model.
    """
    logger.info(f"Running multimodal prompt with model ID: {model_id}")
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": messages
    })

    response = bedrock_runtime.invoke_model(
        body=body, modelId=model_id)
    response_body = json.loads(response.get('body').read())
    logger.info(f"Response: {response_body}")
    return response_body

def extract_workflow_to_mermaid(response):
    logger.info(f"Extracting workflow details from response")
    workflow_details = response['content'][0]['text']  # Adjust based on actual response structure
    # extract the detailed description according to the prompt template
    detailed_description = workflow_details.split("<description>")[1].split("</description>")[0].strip()
    logger.info(f"Extracted detailed description: {detailed_description}")
    # extract the mermaid chart code according to the prompt template
    mermaid_code = workflow_details.split("<mermaid>")[1].split("</mermaid>")[0].strip()
    logger.info(f"Extracted Mermaid code: {mermaid_code}")
    return mermaid_code

"""
Note the schema of content we injected into the Amazon Open Search would be as follows, and we will use the summary & description text and original title to retrieve the representation of the workflow diagram.

original character...
...
<image>
<summary, description text>
</image>
Title 1, picture A

<mermaid>
<summary, description text>
flowchart LR
    A[Start] --Some text--> B(Continue)
    B --> C{Evaluate}
    C -- One --> D[Option 1]
    C -- Two --> E[Option 2]
    C -- Three --> F[fa:fa-car Option 3]
</mermaid>
Title 2 workflow B
...
original character...

"""
if __name__ == "__main__":
    # loop all the image file in the directory with png format to validate the ground truth of the workflow diagram
    for image_path in os.listdir("images"):
        if image_path.endswith(".png"):
            try:
                image_path = os.path.join("images", image_path)
                encoded_image = encode_image(image_path)
                message = {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": encoded_image}},
                        {"type": "text", "text": orignal_template.format(image_data=encoded_image)}
                    ]
                }
                messages = [message]
                response = run_multi_modal_prompt(bedrock_runtime, model_id, messages, max_tokens=4096)
                if response and 'text' in response['content'][0]:
                    mermaid_code = extract_workflow_to_mermaid(response)
            except ClientError as e:
                logger.error(e)
