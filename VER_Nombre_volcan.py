import volcdb
import sys

# Validate input arguments
if len(sys.argv) < 2:
    print("Usage: python VER_Nombre_volcan.py <volcano_name>")
    sys.exit(1)

# Get volcano name from command-line arguments
volcano_name = sys.argv[1]

try:
    # Find the volcano by name
    result = volcdb.find_volcano_by_name(volcano_name)
    
    # Ensure the result is a single entry
    if len(result) == 0:
        print(f"No volcano found with the name '{volcano_name}'.")
        sys.exit(1)
    elif len(result) > 1:
        print(f"Multiple entries found for '{volcano_name}'. Please refine your search.")
        sys.exit(1)
    
    # Extract volcano ID
    volcid = int(result.iloc[0].volc_id)  # Assuming result is a DataFrame or Series
    # Retrieve and print volcano video IDs
    video_ids = volcdb.get_volclip_vids(volcid)
    print(video_ids)

except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
