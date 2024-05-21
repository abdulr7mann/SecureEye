import argparse
import sys
from codeReview import gitCode
from js_scraper import scrape_js_sync

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze code from a GitHub repository or a local path.")
    parser.add_argument('--url', type=str, help="The URL of the GitHub repository to analyze.")
    parser.add_argument('--path', type=str, help="The full path to the local directory to analyze.")
    parser.add_argument('--js', type=str, help="The URL to analyze JS.")
    parser.add_argument('--recursive', action='store_true', help="Enable recursive scraping for JS.")
    args = parser.parse_args()

    try:
        if args.url:
            gitCode.analyze_repository(args.url)
        elif args.path:
            gitCode.analyze_local_path(args.path)
        elif args.js:
            scrape_js_sync(args.js, args.recursive)
        else:
            print("Please provide either a GitHub URL with --url, --js website URL to analyze JS or a local path with --path.")
    except KeyboardInterrupt:
        print("\nApplication interrupted by user. Exiting...")
        sys.exit()
