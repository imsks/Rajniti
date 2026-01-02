# Vidhan Sabha Scraper

This scraper extracts election data from the Election Commission of India's Vidhan Sabha (State Assembly) results pages.

## Usage

### Basic Usage

```bash
python scripts/scrape_vidhan_sabha.py --url <ECI_RESULTS_URL>
```

### Example

For November 2025 elections:

```bash
python scripts/scrape_vidhan_sabha.py --url https://results.eci.gov.in/ResultAcGenNov2025
```

For Delhi Assembly 2025:

```bash
python scripts/scrape_vidhan_sabha.py --url https://results.eci.gov.in/ResultAcGenFeb2025
```

## What It Does

The scraper automatically:
1. **Detects** the state and year from the URL and page content
2. **Scrapes** party-wise results (names, symbols, seats won)
3. **Discovers** all constituencies in the election
4. **Extracts** detailed candidate data (names, parties, votes, margins, images)
5. **Saves** all data as JSON files in the proper structure

## Output

The scraper creates the following files:

```
app/data/
├── vidhan_sabha/
│   └── {STATE}_{YEAR}_ASSEMBLY/
│       ├── parties.json           # Political parties and their performance
│       ├── constituencies.json    # List of constituencies
│       └── candidates.json        # Detailed candidate information
└── elections/
    └── VS-{STATE}-{YEAR}.json    # Election metadata
```

### JSON Structure

#### parties.json
```json
[
  {
    "party_name": "Bharatiya Janata Party",
    "symbol": "Lotus",
    "total_seats": 48
  }
]
```

#### constituencies.json
```json
[
  {
    "constituency_id": "U051",
    "constituency_name": "New Delhi",
    "state_id": "DL"
  }
]
```

#### candidates.json
```json
[
  {
    "uuid": "unique-id",
    "Constituency Code": "U051",
    "Name": "Candidate Name",
    "Party": "Party Name",
    "Status": "WON",
    "Votes": "50000",
    "Margin": "(+5000)",
    "Image URL": "https://..."
  }
]
```

## Features

- **Auto-Detection**: Automatically detects state code and year from URL
- **Robust**: Built-in retry logic and error handling
- **Comprehensive**: Scrapes parties, constituencies, and all candidate details
- **Structured**: Saves data in clean, organized JSON format
- **Progress Logging**: Detailed progress information during scraping

## Testing

Run the test suite:

```bash
pytest tests/test_vidhan_sabha_scraper.py -v
```

## Notes

- The scraper respects server limits with built-in delays
- Network connectivity is required
- Scraping time depends on the number of constituencies (typically 5-15 minutes)
- All data is saved in UTF-8 encoding to properly handle Hindi/regional text

## Troubleshooting

### Connection Errors
If you see connection errors, check:
- Internet connectivity
- ECI website availability
- URL is correct and complete

### No Data Scraped
If no parties/candidates are found:
- Verify the URL is correct
- Check if the election results are declared
- Ensure the page structure hasn't changed

### Missing Dependencies
If you get import errors:
```bash
pip install -r requirements.txt
```
