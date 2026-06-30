# Invoice Line Item Granularity Guide

## Core Principle: Maximum Granularity

**Rule:** Extract EVERY individual charge as a separate line item. Do NOT aggregate or combine.

## Examples

### ❌ WRONG - Aggregated (What you were getting)

```
Invoice DXBR002581849:
  Row 1: EXPRESS WORLDWIDE DOC - 344.71 (BSCHL=40)
  Row 2: Air Waybill 2483071765 - 113.15 (BSCHL=40)  ← WRONG: Combined 4 charges
  Row 3: Air Waybill 2713832866 - 75.39 (BSCHL=40)
  Row 4: Total - 491.57 (BSCHL=31)
```

### ✅ CORRECT - Granular (What you should get)

```
Invoice DXBR002581849:
  Row 1: Base Charge - 79.58 (BSCHL=40)
  Row 2: Integrator Surcharge - 10.29 (BSCHL=40)
  Row 3: Fuel Surcharge - 22.48 (BSCHL=40)
  Row 4: GoGreen Fee - 0.80 (BSCHL=40)
  Row 5: Base Charge - 52.82 (BSCHL=40)
  Row 6: Integrator Surcharge - 6.85 (BSCHL=40)
  Row 7: Fuel Surcharge - 14.92 (BSCHL=40)
  Row 8: GoGreen Fee - 0.80 (BSCHL=40)
  ... (continue for all charges)
  Row N: Total - 491.57 (BSCHL=31)
```

## Common Scenarios

### Scenario 1: DHL Invoice with Surcharges

**PDF Shows:**
```
Air Waybill: 2483071765
Weight Charge: 79.58
INTEGRATOR SURCHARGE: 10.29
FUEL SURCHARGE: 22.48
GOGREEN PLUS: 0.80
Total: 113.15
```

**Extract as 5 line items:**
1. Weight Charge - 79.58
2. Integrator Surcharge - 10.29
3. Fuel Surcharge - 22.48
4. GoGreen Plus - 0.80
5. Total - 113.15

### Scenario 2: Travel Invoice with Multiple Fees

**PDF Shows:**
```
Base Fare: 2,000
Airport Tax: 540
Corp Transaction Fee: 157
Total: 2,697
```

**Extract as 4 line items:**
1. Base Fare - 2,000
2. Airport Tax - 540
3. Corp Transaction Fee - 157
4. Total - 2,697

### Scenario 3: Certificate of Origin Invoice

**PDF Shows:**
```
Certificate of Origin (28 units @ 100): 2,800
Service Charges (28 units @ 100): 2,800
Tax (5%): 140
Total: 5,740
```

**Extract as 4 line items:**
1. Certificate of Origin - 2,800
2. Service Charges - 2,800
3. Tax - 140
4. Total - 5,740

## Why Granularity Matters

1. **Accounting Accuracy**: Each charge may map to different GL accounts
2. **Cost Analysis**: Allows breakdown of costs by type
3. **Audit Trail**: Clear visibility of all charges
4. **Reconciliation**: Easier to match with source documents

## What NOT to Do

### ❌ Don't Combine
- Base + Surcharges into one line
- Multiple fees into "Total Fees"
- Tax + Amount into one line

### ❌ Don't Summarize
- "Various charges - 113.15"
- "Service charges (summary) - 344.71"
- "Multiple surcharges - 33.57"

### ✅ Do Extract Separately
- Each base charge
- Each surcharge (fuel, integrator, etc.)
- Each fee (transaction, service, etc.)
- Each tax line
- Final total

## LLM Instructions Summary

The system now explicitly instructs the LLM:
1. "Extract EVERY individual charge/line item separately"
2. "Do NOT aggregate or summarize"
3. "Each charge, fee, surcharge, tax should be its own line item"
4. "Do NOT combine multiple charges into one line"

## Validation

After extraction, verify:
- Number of line items matches number of charges in PDF
- Sum of individual charges equals the total
- No aggregated descriptions like "base + surcharges"
- Each charge has its own row with BSCHL=40
- Only the final total has BSCHL=31
