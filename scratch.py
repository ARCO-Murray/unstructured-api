import argparse
import time
import json
from unstructured.partition.pdf import partition_pdf
from unstructured.staging.base import convert_to_isd

# Set up argument parser
parser = argparse.ArgumentParser(description="Print source and destination filenames.")
parser.add_argument("source", type=str, help="The source file name")
parser.add_argument("destination", type=str, help="The destination file name")
parser.add_argument("strategy", type=str, help="The partition strategy", default="auto")

# Parse the arguments
args = parser.parse_args()

# Print the source and destination file names
print(f"Source file: {args.source}")
print(f"Destination file: {args.destination}")
print(f"Strategy: {args.strategy}")

start = time.time()
elements = partition_pdf(filename=args.source, strategy=args.strategy)
result = convert_to_isd(elements)
print(f"took {time.time() - start} seconds")

with open(args.destination, "w") as file:
    json.dump(result, file)
    print(f"from {args.source} result of len {len(result)} written to {args.destination}")
