# Q1: FIFA World Cup Data Extraction

## Task

Extract structured tabular data from the FIFA World Cup Wikipedia page into Google Sheets using formulas to analyze historical team and player statistics.

---

## Requirements

* Retrieve data from the "Teams reaching the top four" table
* Retrieve data from the "Top goalscorers" table
* Determine the total number of World Cups Germany has won
* Determine the total number of World Cup goals Ronaldo scored
* Format the output as a comma-separated string (e.g., "4, 15")

---

## Approach

### 1. Identify Source Data
Locate the target tables on the Wikipedia page to determine their relative positions for extraction.

### 2. Import Teams Table
Use the `IMPORTHTML` function in Google Sheets to pull the team performance statistics.

### 3. Import Scorers Table
Use the `IMPORTHTML` function in a separate sheet to pull the individual player statistics.

### 4. Query Germany's Wins
Utilize lookup formulas (`VLOOKUP`) or filters to extract the specific value from the "Winners" column for Germany.

### 5. Query Ronaldo's Goals
Utilize lookup formulas to extract the total goals value for Ronaldo from the goalscorers table.

### 6. Format Final Result
Combine the two numerical results into a single comma-separated string for submission.

---

## Execution

### Step 1: Import Data into Google Sheets

**Extract Teams Table:**
```excel
=IMPORTHTML("https://en.wikipedia.org/wiki/FIFA_World_Cup", "table", 4)
```
*Note: The table index (4) may vary based on page layout updates. Adjust the index if the incorrect table loads.*

**Extract Goalscorers Table:**
```excel
=IMPORTHTML("https://en.wikipedia.org/wiki/FIFA_World_Cup", "table", 8)
```
*Note: Adjust this index (8) similarly if needed.*

### Step 2: Query Extracted Data

**Find Germany's Wins:**
Assuming the Teams table is loaded in `Sheet1!A:F`, and "Winners" is the second column:
```excel
=VLOOKUP("Germany*", Sheet1!A:F, 2, FALSE)
```
*Expected Result: 4*

**Find Ronaldo's Goals:**
Assuming the Scorers table is loaded in `Sheet2!A:E`, and "Goals" is the third column:
```excel
=VLOOKUP("Ronaldo", Sheet2!A:E, 3, FALSE)
```
*Expected Result: 15*

---

## Verification

### Automated Extraction Script (Alternative)
For programmatic verification without Google Sheets, data can be extracted using Python:

**Dependencies:**
```powershell
pip install requests beautifulsoup4
```

**Extraction Logic:**
1. Fetch HTML via `requests.get()`
2. Parse DOM with `BeautifulSoup`
3. Locate headers "Teams reaching the top four" and "Top goalscorers"
4. Iterate over adjacent `<table>` rows matching 'Germany' and 'Ronaldo'

**Script Output:**
```
--- Teams reaching the top four ---
['Germany', '[WINS] (..., ...)', ...]

--- Top goalscorers ---
['[RANK]', 'Ronaldo', '[GOALS]', '[MATCHES]', '[RATIO]']
```

---

## Submission

**Your Answer:**
```
[WINS], [GOALS]
```

Copy the comma-separated numbers and submit them to the assignment platform. The results will confirm Germany's wins and Ronaldo's goals.
