## Background
To use AWS Bedrock (Claude 3) to identify the content of an image with a flow inside a diagram, extract the detailed object workflow, and transform it into Mermaid chart code, you need to follow several steps. This involves leveraging the multi-modal capabilities of Claude 3, setting up the proper prompt template, and invoking the model API. Below is a detailed guide with sample code.

## Core Components
- Multi-modal Capability API Invocation: This involves invoking the AWS Bedrock model with a multimodal prompt that includes the image data.
- Proper Prompt Template: Crafting an appropriate prompt to guide the model in identifying and extracting the necessary information from the image.
- Transformation to Mermaid Chart Code: Converting the extracted workflow details into Mermaid chart code.

## Notes
original character
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

<image>
    <summary, description text>
    pie chart, that was not optimzed in mermaid
</image>
Title 3 workflow C
...
original character


<description>
This pie chart represents the process of pet adoption by volunteers, illustrating the distribution of different types of pets adopted. The diagram is a pie chart with the following details:

Title:

"Pets adopted by volunteers"
Categories:

Dogs: Represented by a large section of the pie chart, accounting for 79% of the total adoptions.
Cats: Represented by a mid-sized section, accounting for 17% of the total adoptions.
Rats: Represented by a small section, accounting for 3% of the total adoptions.
Legend:

The legend on the right side of the chart uses different shades of green to differentiate between the categories:
Light green for Dogs.
Medium green for Cats.
Dark green for Rats.
The pie chart visually demonstrates the proportion of each type of pet adopted by volunteers, with the majority being dogs, followed by cats and a small percentage of rats.
</description>

<mermaid>
pie title Pets adopted by volunteers
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15
</mermaid>


<description>
This quadrant chart represents the process of evaluating the reach and engagement of various campaigns that categorizes campaigns based on their reach (horizontal axis) and engagement (vertical axis). The chart is divided into four quadrants, each representing a different strategy for the campaigns:

1. **Quadrants**:
    - **Need to promote** (High Engagement, Low Reach):
        - Campaign F
        - Campaign A
    - **We should expand** (High Engagement, High Reach):
        - Campaign C
    - **Re-evaluate** (Low Engagement, Low Reach):
        - Campaign E
        - Campaign B
    - **May be improved** (Low Engagement, High Reach):
        - Campaign D

2. **Axes**:
    - **Vertical Axis**: Represents Engagement, ranging from Low Engagement at the bottom to High Engagement at the top.
    - **Horizontal Axis**: Represents Reach, ranging from Low Reach on the left to High Reach on the right.

3. **Campaigns**:
    - Each campaign is represented by a black dot and labeled accordingly:
        - Campaign A, B, C, D, E, and F.

4. **Labels**:
    - Each quadrant is labeled to indicate the suggested action for the campaigns within it:
        - "Need to promote" for campaigns with high engagement but low reach.
        - "We should expand" for campaigns with both high engagement and high reach.
        - "Re-evaluate" for campaigns with both low engagement and low reach.
        - "May be improved" for campaigns with high reach but low engagement.

The quadrant chart visually demonstrates the performance of each campaign in terms of reach and engagement, helping to identify which campaigns need more promotion, which should be expanded, which need re-evaluation, and which may be improved.
</description>

<mermaid>
quadrantChart
    title Reach and engagement of campaigns
    x-axis Low Reach --> High Reach
    y-axis Low Engagement --> High Engagement
    quadrant-1 We should expand
    quadrant-2 Need to promote
    quadrant-3 Re-evaluate
    quadrant-4 May be improved
    Campaign A: [0.3, 0.6]
    Campaign B: [0.45, 0.23]
    Campaign C: [0.57, 0.69]
    Campaign D: [0.78, 0.34]
    Campaign E: [0.40, 0.34]
    Campaign F: [0.35, 0.78]
</mermaid>    