import argparse
import os
from builder import RytonBuilder
import sys

def main():
    print("RytonBuilder CLI starting...", flush=True)
    
    parser = argparse.ArgumentParser(description='Ryton Project Builder')
    
    parser.add_argument('command', choices=['build', 'clean'])
    parser.add_argument('main_file', nargs='?', help='Entry point .ry file')
    parser.add_argument('--output', '-o', default='app',
                       help='Output executable name')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed build information')
    
    print("Parsing arguments...", flush=True)
    args = parser.parse_args()
    
    print(f"Command: {args.command}", flush=True)
    print(f"Main file: {args.main_file}", flush=True)
    
    builder = RytonBuilder(os.getcwd())
    
    if args.command == 'build':
        print("Starting build process...", flush=True)
        success = builder.build(args.main_file, args.output, verbose=args.verbose)
        code = 0 if success else 1
        print(f"Build finished with code {code}", flush=True)
        sys.exit(code)

if __name__ == '__main__':
    main()
