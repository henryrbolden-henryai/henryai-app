# CSV Parser Fix

**Priority:** Critical  
**Scope:** Replace `parseLinkedInCSV()` in `outreach.html`  
**Dependency:** None  
**Blocks:** All network intelligence features

---

## The Problem

Current parser (line 1104-1124 in outreach.html):

```javascript
function parseLinkedInCSV(csv) {
    const lines = csv.split('\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
        // BREAKS HERE: "Director, Engineering" becomes ["Director", "Engineering"]
    }
}
```

This corrupts any row where Company or Position contains a comma. Given that titles like "Director, Product" and companies like "Google, LLC" are common, a significant percentage of connections are silently corrupted.

---

## The Fix

### Step 1: Add PapaParse to `<head>`

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>
```

### Step 2: Replace `parseLinkedInCSV` function

Find and replace the entire function (lines 1103-1124) with:

```javascript
// Parse LinkedIn CSV - handles quoted fields with commas correctly
function parseLinkedInCSV(csv) {
    const result = Papa.parse(csv, {
        header: true,
        skipEmptyLines: true,
        transformHeader: h => h.trim()
    });
    
    // Filter out empty rows (LinkedIn exports sometimes have blank lines)
    return result.data.filter(row => 
        (row['First Name'] && row['First Name'].trim()) || 
        (row['Last Name'] && row['Last Name'].trim())
    );
}
```

That's it. 11 lines replaced with 10 lines that actually work.

---

## Validation Test

Add this temporary test function to verify the fix. Run it once after implementation, then remove.

```javascript
// TEMPORARY: Run this in browser console after uploading a CSV to validate parsing
function validateCSVParsing() {
    const testCSV = `First Name,Last Name,URL,Email Address,Company,Position,Connected On
John,Smith,https://linkedin.com/in/john,john@test.com,"Google, LLC","Director, Engineering",01 Jan 2025
Jane,Doe,https://linkedin.com/in/jane,,"Acme Corp","Senior Manager, Product",15 Dec 2024
"Mary Ann",Johnson,https://linkedin.com/in/maryann,,"""Quoted"" Company",CEO,01 Jun 2020`;

    const parsed = parseLinkedInCSV(testCSV);
    
    const tests = [
        {
            name: 'Row count',
            pass: parsed.length === 3,
            expected: 3,
            actual: parsed.length
        },
        {
            name: 'Company with comma',
            pass: parsed[0]['Company'] === 'Google, LLC',
            expected: 'Google, LLC',
            actual: parsed[0]['Company']
        },
        {
            name: 'Position with comma',
            pass: parsed[0]['Position'] === 'Director, Engineering',
            expected: 'Director, Engineering',
            actual: parsed[0]['Position']
        },
        {
            name: 'Email preserved',
            pass: parsed[0]['Email Address'] === 'john@test.com',
            expected: 'john@test.com',
            actual: parsed[0]['Email Address']
        },
        {
            name: 'Empty email handled',
            pass: parsed[1]['Email Address'] === '',
            expected: '(empty string)',
            actual: parsed[1]['Email Address'] || '(empty string)'
        },
        {
            name: 'Quoted first name',
            pass: parsed[2]['First Name'] === 'Mary Ann',
            expected: 'Mary Ann',
            actual: parsed[2]['First Name']
        },
        {
            name: 'Escaped quotes in company',
            pass: parsed[2]['Company'] === '"Quoted" Company',
            expected: '"Quoted" Company',
            actual: parsed[2]['Company']
        }
    ];
    
    console.log('=== CSV Parser Validation ===');
    let allPass = true;
    tests.forEach(t => {
        const status = t.pass ? '✓' : '✗';
        console.log(`${status} ${t.name}: expected "${t.expected}", got "${t.actual}"`);
        if (!t.pass) allPass = false;
    });
    console.log(allPass ? '\n✓ All tests passed' : '\n✗ Some tests failed');
    
    return allPass;
}

// Run: validateCSVParsing()
```

---

## Implementation Checklist

- [ ] Add PapaParse CDN link to `<head>` section of outreach.html
- [ ] Replace `parseLinkedInCSV` function (lines 1103-1124)
- [ ] Open browser console, run `validateCSVParsing()`, confirm all tests pass
- [ ] Upload a real LinkedIn CSV export, verify connections display correctly
- [ ] Remove `validateCSVParsing` function (test code, not for production)

---

## What This Unblocks

Once merged, the following features can trust the underlying data:

1. Recency sorting (Connected On is now reliable)
2. Email-based outreach paths (Email Address is now reliable)
3. Recruiter/seniority detection (Position is now reliable)
4. Company matching (Company is now reliable)
5. Hey Henry network intelligence (all fields are now reliable)

None of those should be built until this lands.
