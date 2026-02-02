#!/usr/bin/env python3
"""
DEPRECATED: This script is kept for backward compatibility.

Please use the generic election scraper instead:
    python scripts/scrape_election.py --url <URL> --type vidhan-sabha

This script delegates to the generic scraper with vidhan-sabha type.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == "__main__":
    # Import here to avoid circular issues
    import scripts.scrape_election as scrape_election_module
    
    # Add --type vidhan-sabha to sys.argv if not present
    if "--type" not in sys.argv:
        # Find where --url is and insert after it
        url_idx = None
        for i, arg in enumerate(sys.argv):
            if arg == "--url" and i + 1 < len(sys.argv):
                url_idx = i + 2
                break
        
        if url_idx:
            sys.argv.insert(url_idx, "--type")
            sys.argv.insert(url_idx + 1, "vidhan-sabha")
        else:
            # If --url not found, add both
            sys.argv.extend(["--type", "vidhan-sabha"])
    
    # Call the main function from the generic scraper
    scrape_election_module.main()
