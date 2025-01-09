import sys
import os
from argparse import ArgumentParser
from pathlib import Path

current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))

from translator import translate_file


def main():
    parser = ArgumentParser(description='Translate Java code to C++')
    parser.add_argument('input', help='Input Java file path')
    parser.add_argument('-o', '--output', help='Output C++ file path (optional)')

    args = parser.parse_args()

    input_path = os.path.abspath(args.input)

    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist")
        sys.exit(1)

    if not args.output:
        output_path = os.path.splitext(input_path)[0] + '.cpp'
    else:
        output_path = os.path.abspath(args.output)

    print(f"Translating {input_path} to {output_path}...")

    if translate_file(input_path, output_path):
        print("Translation completed successfully!")
    else:
        print("Translation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()