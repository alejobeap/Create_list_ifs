
import numpy as np
import matplotlib.pyplot as plt
import os

# File name
file_name = 'Longs_combination_average_cc.txt'

# Initialize lists to store data
data_values = []

# Read the file
with open(file_name, 'r') as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) == 2:
            try:
                value = float(parts[1])
                data_values.append(value)
            except ValueError:
                # Skip lines with 'nan' or non-numeric values
                continue

# Convert to NumPy array
data_values = np.array(data_values)

# Calculate mean and standard deviation
mean_value = np.nanmean(data_values)
std_value = np.nanstd(data_values)

# Print mean and standard deviation
print(f"Mean: {mean_value:.4f}")
print(f"Standard Deviation: {std_value:.4f}")

# Plot histogram
plt.figure(figsize=(8, 6))
plt.hist(data_values, bins=15, color='blue', alpha=0.7, edgecolor='black')

plt.title('Histogram of longs IFS')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Save the figure
current_directory = os.getcwd()
# Extract parts of the directory for naming
path_parts = current_directory.split(os.sep)
if len(path_parts) >= 2:
    location_name = path_parts[-2]
    batch_name = path_parts[-1]
else:
    location_name = "Unknown"
    batch_name = "Unknown"
output_filename = f"Long_histogram_{location_name}_{batch_name}.png"
output_path = os.path.join(current_directory, output_filename)

plt.savefig(output_path, dpi=300)

