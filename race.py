import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Purdue brand colors, excluding black
brand_colors = [
    '#CFB991',  # Boilermaker Gold
    '#8E6F3E',  # Aged Gold
    '#DAAA00',  # Rush
    '#DDB945',  # Field
    '#EBD99F',  # Dust
    '#9D9795',  # Railway Gray
    '#C4BFC0'   # Steam
]

# Load the data from the CSV file
df = pd.read_csv('race.csv', encoding='utf-16', sep=None, engine='python')

# Find the latest period which should be the last valid column representing a year
latest_period = df.columns[-1]

# Filter rows that contain the 'FTE Headcount Control' for all categories
fte_headcount_control = df[df['Unnamed: 1'].str.contains('FTE Headcount Control', na=False)]

# Extract the headcount numbers for the latest period for all categories
latest_headcount_data = fte_headcount_control[latest_period].str.replace(',', '').astype(float)

# Calculate the total headcount to find the percentages
total_headcount = latest_headcount_data.sum()

# Calculate the percentages for each category
percentages = (latest_headcount_data / total_headcount) * 100

# Round to three significant figures where the value is not zero
percentages = percentages.apply(lambda x: round(x, -int(np.floor(np.log10(abs(x)))) + 2) if x != 0 else x)

# Extract the category names
categories = fte_headcount_control['Color_Variable']

# Colors need to match the number of categories we have
colors = (brand_colors * (len(categories) // len(brand_colors) + 1))[:len(categories)]

# Increase the figure size for better label spacing and create the pie chart
fig, ax = plt.subplots(figsize=(10, 10))
wedges, texts, autotexts = ax.pie(
    percentages.values, 
    colors=colors, 
    autopct='%1.0f%%', 
    startangle=90, 
    pctdistance=0.8  # Position the percentage closer to the center
)

# Draw a circle at the center of pie to make it a donut
centre_circle = plt.Circle((0, 0), 0.60, fc='white')
fig.gca().add_artist(centre_circle)

# Increase the font size of the autotexts (percentages) and adjust positions if needed
for i, autotext in enumerate(autotexts):
    autotext.set_size('x-large')
    # Check for specific categories that need position adjustments
    if categories.values[i] in ['Unknown']:
        # Adjust the position of the percentage label
        autotext.set_position((autotext.get_position()[0] * 1.1, autotext.get_position()[1] * 1.1))


# Manually adjust the positions of labels that are overlapping
adjustments = {
    '2 or more races': {'xytext': (1.5, 1.6)},
    'Unknown': {'xytext': (1.5, -1.6)},
    'Native Hawaiian or Other Pacific Islander': {'xytext': (-1.5, -1.6)},
    'American Indian or Alaska Native': {'xytext': (-1.5, 1.6)}
}

# Calculate the angle for each wedge to place the labels and draw lines
for i, wedge in enumerate(wedges):
    ang = (wedge.theta2 - wedge.theta1) / 2. + wedge.theta1
    x = np.cos(np.deg2rad(ang))
    y = np.sin(np.deg2rad(ang))

    # Check if this category needs adjustment
    if categories.values[i] in adjustments:
        xytext = adjustments[categories.values[i]]['xytext']
    else:
        # Use default placement for other categories
        xytext = (1.35*np.sign(x), 1.4*y)

    horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
    connectionstyle = f"angle,angleA=0,angleB={ang}"
    kw = dict(arrowprops=dict(arrowstyle="-", connectionstyle=connectionstyle, color=colors[i]),
              bbox=dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72),
              zorder=0, va="center", size='large')

    ax.annotate(categories.values[i], xy=(x, y), xytext=xytext,
                horizontalalignment=horizontalalignment, **kw)

ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
image_name = f'{latest_period}_fte_headcount_comparison_updated_labels.png'
plt.savefig(image_name)

# Show the plot
plt.show()

# Create a separate plot to show Latino/Hispanic population against the rest
hispanic_percentage = percentages[categories == 'Hispanic/Latino'].iloc[0]
non_hispanic_percentage = 100 - hispanic_percentage
hispanic_colors = ['#DDB945', '#9D9795']  # Colors for Hispanic/Latino vs the rest
fig1, ax1 = plt.subplots(figsize=(7, 7))
ax1.pie(
    [hispanic_percentage, non_hispanic_percentage],
    labels=['Hispanic/Latino', 'Other'],
    colors=hispanic_colors,
    autopct='%1.1f%%',
    startangle=90
)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
hispanic_image_name = f'{latest_period}_hispanic_vs_rest_separate.png'
plt.savefig(hispanic_image_name)

# Create a separate column plot to showcase the differences between races FTE students numbers
fig2, ax2 = plt.subplots(figsize=(10, 11))
ax2.bar(categories.values, latest_headcount_data.values, color=colors)
ax2.set_ylabel('FTE Headcount')
ax2.set_title('FTE Headcount by Race')
ax2.set_xticklabels(categories.values, rotation=45, ha='right')
column_plot_image_name = f'{latest_period}_fte_numbers_comparison_separate.png'
plt.savefig(column_plot_image_name)

plt.show()