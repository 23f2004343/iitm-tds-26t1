# Q14: Web Scraping with Playwright

## Task

Extract and sum data from multiple HTML tables across pages using Playwright.

---

## Requirements

* Use Playwright to extract data from HTML tables
* Handle pagination or iterate over a sequence of URLs (Seeds 25-34)
* Extract numeric values and compute the sum of all numbers in all tables
* Output the final total sum

---

## Approach

### 1. Setup Environment
Install the necessary Playwright packages to automate browser interactions.

### 2. Write Extraction Script
Develop an asynchronous Python script to launch Chromium, navigate to each target URL, and wait for the tables to render.

### 3. Parse Table Content
Use Playwright's page evaluation context to run JavaScript that extracts and cleanly parses all numeric values within `<td>` and `<th>` elements.

### 4. Aggregate Totals
Iterate through the specified seeds, sum the results locally, and print the overall total.

---

## Execution

### Step 1: Install Dependencies

**Requirements:**
```bash
pip install playwright
playwright install chromium
```

### Step 2: Running the Scraper

Execute the provided Python script to perform the data extraction:

```bash
python solve.py
```

*Note: The script accesses seeds 25 through 34 and aggregates the total sum programmatically.*

---

## Submission

**Your Answer:**
```
2550034
```

Copy the final calculated sum and submit it to the assignment platform.
