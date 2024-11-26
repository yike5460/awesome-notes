import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle, Patch

# Define request and response directives with descriptions
request_directives = ['no-cache', 'max-age=0', 'max-stale', 'min-fresh', 'only-if-cached']
request_desc = [
    'Force validation',
    'Require fresh content',
    'Accept stale content',
    'Ensure minimum freshness',
    'Use cache only'
]

response_directives = ['no-store', 'no-cache', 'private', 'public', 'max-age=3600', 'must-revalidate', 's-maxage=7200']
response_desc = [
    'Never cache',
    'Validate before use',
    'Personal cache only',
    'Public cacheable',
    'Cache for 1 hour',
    'Strict validation',
    'CDN cache for 2 hours'
]

# Create interaction matrix with descriptions and use cases
matrix_data = []
annotations = []

for i in range(len(request_directives)):
    row_data = []
    row_annotations = []
    for j in range(len(response_directives)):
        strength = 0
        desc = "L: -\nR: -\nCase: -"  # Default description
        
        # Define interactions, effects, and use cases
        if request_directives[i] == 'no-cache':
            if response_directives[j] == 'no-store':
                strength = 2
                desc = "L: No storage\nR: No storage\nCase: Sensitive data"
            elif response_directives[j] == 'no-cache':
                strength = 3
                desc = "L: Must validate\nR: Fresh content\nCase: Real-time data"
            elif response_directives[j] == 'private':
                strength = 1
                desc = "L: Private only\nR: No shared\nCase: User profile"
            elif response_directives[j] == 'must-revalidate':
                strength = 3
                desc = "L: Strict validate\nR: Origin check\nCase: Banking data"
        
        elif request_directives[i] == 'max-age=0':
            if response_directives[j] == 'max-age=3600':
                strength = 1
                desc = "L: No cache\nR: Server cache\nCase: News feed"
            elif response_directives[j] == 's-maxage=7200':
                strength = 1
                desc = "L: No cache\nR: CDN active\nCase: API gateway"
            elif response_directives[j] == 'must-revalidate':
                strength = 3
                desc = "L: Always validate\nR: Strict\nCase: Stock prices"
        
        elif request_directives[i] == 'max-stale':
            if response_directives[j] == 'public':
                strength = 2
                desc = "L: Use stale OK\nR: Shared\nCase: Blog posts"
            elif response_directives[j] == 'max-age=3600':
                strength = 3
                desc = "L: Extend time\nR: Normal\nCase: Static content"
            elif response_directives[j] == 's-maxage=7200':
                strength = 3
                desc = "L: Flexible\nR: CDN extend\nCase: Images/CSS"
        
        elif request_directives[i] == 'min-fresh':
            if response_directives[j] == 'max-age=3600':
                strength = 3
                desc = "L: Min fresh\nR: Age limit\nCase: Weather data"
            elif response_directives[j] == 's-maxage=7200':
                strength = 3
                desc = "L: Fresh guard\nR: CDN fresh\nCase: API data"
        
        elif request_directives[i] == 'only-if-cached':
            if response_directives[j] == 'public':
                strength = 3
                desc = "L: Cache only\nR: Shared OK\nCase: Offline mode"
            elif response_directives[j] == 'max-age=3600':
                strength = 3
                desc = "L: Use cache\nR: Time limit\nCase: Quick load"
            elif response_directives[j] == 's-maxage=7200':
                strength = 3
                desc = "L: Local only\nR: CDN cache\nCase: Static assets"
        
        row_data.append(strength)
        row_annotations.append(desc)
    matrix_data.append(row_data)
    annotations.append(row_annotations)

# Create figure and axis with more space for labels
plt.figure(figsize=(24, 16))
ax = plt.gca()

# Create heatmap
sns.heatmap(matrix_data, annot=False, cmap='YlOrRd', 
            cbar_kws={'label': 'Interaction Strength (0-3)'})

# Add text annotations with larger font size
for i in range(len(request_directives)):
    for j in range(len(response_directives)):
        strength = matrix_data[i][j]
        if strength > 0:  # Only show descriptions for non-zero interactions
            text = f"Strength: {strength}\n{annotations[i][j]}"
            ax.text(j + 0.5, i + 0.5, text,
                   ha='center', va='center',
                   fontsize=10)  # Increased font size from 8 to 10

# Add scenario groupings with thicker dotted lines
# Real-time data scenario
ax.add_patch(Rectangle((0, 0), 3, 1, fill=False, linestyle=':', color='blue', linewidth=2.5))
# Static content scenario
ax.add_patch(Rectangle((3, 2), 3, 1, fill=False, linestyle=':', color='green', linewidth=2.5))
# API/CDN scenario
ax.add_patch(Rectangle((5, 1), 2, 2, fill=False, linestyle=':', color='red', linewidth=2.5))

# Add legend for scenarios with larger font
legend_elements = [
    Patch(facecolor='none', edgecolor='blue', linestyle=':', label='Real-time Data Flow'),
    Patch(facecolor='none', edgecolor='green', linestyle=':', label='Static Content Delivery'),
    Patch(facecolor='none', edgecolor='red', linestyle=':', label='API/CDN Optimization')
]
ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.3, 1), fontsize=12)

plt.title('Cache-Control Directive Interaction Matrix\nwith Local (L) and Remote (R) Cache Effects and Use Cases', 
         pad=20, fontsize=14)

# Create more readable x-axis labels
x_labels = [f'{d} - {desc}' for d, desc in zip(response_directives, response_desc)]
y_labels = [f'{d} - {desc}' for d, desc in zip(request_directives, request_desc)]

# Set axis labels with adjusted position, rotation, and larger font size
ax.set_xticks(np.arange(len(response_directives)) + 0.5)
ax.set_xticklabels(x_labels, rotation=30, ha='right', fontsize=12)

ax.set_yticks(np.arange(len(request_directives)) + 0.5)
ax.set_yticklabels(y_labels, rotation=0, ha='right', fontsize=12)

# Add axis labels
plt.xlabel('Response Directives', fontsize=14, labelpad=20)
plt.ylabel('Request Directives', fontsize=14, labelpad=20)

# Adjust layout to prevent label cutoff
plt.tight_layout()
plt.show()