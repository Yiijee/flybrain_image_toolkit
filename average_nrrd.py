import os
import sys
import numpy as np
import nrrd
# for a given folder, average all nrrd stacks
def read_nrrd(file_path):
    data, header = nrrd.read(file_path)
    return data, header

def average_nrrd_images(folder_path):
    # Get all nrrd files in the folder
    nrrd_files = [f for f in os.listdir(folder_path) if f.endswith('.nrrd')]
    print(f"Found {len(nrrd_files)} nrrd files in the folder.")
    if not nrrd_files:
        print("No nrrd files found in the folder.")
        return

    import concurrent.futures
    # Read and accumulate all nrrd images in parallel
    accumulated_image = None
    count = 0
    file_paths = [os.path.join(folder_path, nrrd_file) for nrrd_file in nrrd_files]
    headers = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(read_nrrd, file_paths))

    for data, header in results:
        if accumulated_image is None:
            accumulated_image = np.zeros_like(data, dtype=np.float32)
            headers.append(header)  # Save the header of the first file
        accumulated_image += data
        count += 1
        print(f"Accumulated {count} images.")

    # Compute the average
    averaged_image = accumulated_image / count
    print(f"Averaged {count} images.")

    # Save the averaged image in a subfolder
    print("Saving averaged image...")
    output_folder = os.path.join(folder_path, "averaged_output")
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "averaged_image.nrrd")
    nrrd.write(output_path, averaged_image.astype(np.float32), headers[0], compression_level=1)
    print(f"Averaged image saved to: {output_path}")

# Example usage
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python average_nrrd.py <folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    average_nrrd_images(folder_path)