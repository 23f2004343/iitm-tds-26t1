# Q6: Data Sourcing with Google Dorks

## Task

Construct a single Google Dork query that surfaces Excel budget files from 2020 on the `gov.in` domain.

---

## Requirements

* Target the domain `gov.in`.
* Target specific downloadable dataset formats (Excel).
* Use keywords to find files related to "budget" and "2020".
* The query must be at least 35 characters long.

---

## Approach

### 1. Domain Targeting
Use the `site:` operator to restrict searches.
**Operator:** `site:gov.in`

### 2. File Discovery
Use the `filetype:` or `ext:` operator to find Excel files.
**Operator:** `filetype:xlsx` (or `.xls`)

### 3. Keyword Precision
Use the `intext:` or `intitle:` operators to search for the specific terms.
**Operator:** `intext:budget 2020` or `intitle:budget intext:2020`

### 4. Combine and Verify Length
Combine the operators into a single string.
`site:gov.in filetype:xlsx intext:budget 2020`
Length: 44 characters (satisfies the >35 character requirement).

---

## Execution

The synthesized query filters all indexed pages to return only Excel files on the Indian government domain that contain the words "budget" and "2020".

---

## Submission

**Your Answer:**
```
site:gov.in filetype:xlsx intext:budget 2020
```

Copy the search query and submit it to the assignment platform.
