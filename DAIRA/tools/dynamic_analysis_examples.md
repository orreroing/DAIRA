# Dynamic Analysis Tool Examples

Generated at: 2026-05-26T13:26:26

This report runs one standalone example for each newly added non-Python dynamic analysis tool.
For every language, it records the reproduction input, raw tool output, and the native output from `sweagent.agent.trace_summary.handle_trace_log`.

## Java

Tool: `run_java_trace`

Notes: Uses Java Flight Recorder execution samples to capture sampled call stacks. This is sampling-based, not exact method enter/return tracing.

### Command

````bash
tools/java_dynamic_analysis_tool/bin/run_java_trace 'javac /tmp/JavaTraceDemo.java && java -cp /tmp JavaTraceDemo' JavaTraceDemo checkout 12
````

### Input

````text
public class JavaTraceDemo {
    public static void main(String[] args) {
        long total = 0;
        for (int i = 0; i < 200000; i++) {
            total += checkout(i);
        }
        System.out.println(total);
    }

    static long checkout(int seed) {
        return sumItems(seed) - discount(seed);
    }

    static long sumItems(int seed) {
        long result = 0;
        for (int i = 0; i < 80; i++) {
            result += normalizePrice(seed + i);
        }
        return result;
    }

    static long normalizePrice(int value) {
        long result = value;
        for (int i = 0; i < 20; i++) {
            result = (result * 31 + i) % 9973;
        }
        return result;
    }

    static long discount(int seed) {
        return seed % 17;
    }
}
````

### Raw Dynamic Analysis Output

````text
--- Starting Java Flight Recorder trace ---
Run command: javac /tmp/JavaTraceDemo.java && java -cp /tmp JavaTraceDemo
Class/package filter: JavaTraceDemo
Local tracking method: checkout

--- Target command console output ---
Started recording 1. No limit specified, using maxsize=250MB as default.

Use jcmd 50 JFR.dump name=1 to copy recording data to file.
79774058225
--- Target command stderr ---
NOTE: Picked up JDK_JAVA_OPTIONS: -XX:StartFlightRecording=filename=/tmp/sweagent-java-trace-82ubfdig/trace.jfr,settings=profile,dumponexit=true,disk=true
--- Target command console output ended ---

* **target_language:** `java`
* **run_command:** `javac /tmp/JavaTraceDemo.java && java -cp /tmp JavaTraceDemo`
* **class_filter:** `JavaTraceDemo`
* **method_to_trace:** `checkout`
* **trace_depth:** `12`
* **Filter Level:** Java Flight Recorder execution samples around frames matching the class/method filters.
* **Trace Type:** Sampling-based JFR stack trace, not exact method enter/return instrumentation.

<trace_log>
```text
0001 SAMPLE_STACK hits=25
     FRAME  JavaTraceDemo.sumItems(int) line: 16
       TARGET JavaTraceDemo.checkout(int) line: 11
         FRAME  JavaTraceDemo.main(String[]) line: 5
```
</trace_log>
````

### Native LLM Summary Output

````text
# Execution Workflow Analysis Report

## 1. Initial Representation
**Input:** Integer value `79774058225` (passed to `checkout` method)

## 2. Top-Level Call
```
JavaTraceDemo.main(String[]) -> JavaTraceDemo.checkout(int)
```

## 3. Execution Tree (Sampling-Based JFR Trace)

```
(1) JavaTraceDemo.main(String[]) [line: 5]
    |
    `-- (2) JavaTraceDemo.checkout(int) [line: 11]
        |
        `-- (3) JavaTraceDemo.sumItems(int) [line: 16]
```

The trace shows the hottest stack frame captured during execution. Because the trace is sampled by JFR, it should be used for locating relevant runtime context rather than proving exact call/return counts.
````

## Ruby

Tool: `run_ruby_trace`

Notes: Uses Ruby TracePoint to capture call, return, and raise events.

### Command

````bash
tools/ruby_dynamic_analysis_tool/bin/run_ruby_trace /tmp/ruby_trace_branch_demo.rb ruby_trace_branch_demo total 12
````

### Input

````text
class DiscountCalculator
  def total(items, coupon)
    subtotal = sum_items(items)
    discount = coupon_discount(coupon)
    subtotal - discount
  rescue ArgumentError
    subtotal
  end

  def sum_items(items)
    items.map { |item| normalize_price(item) }.sum
  end

  def normalize_price(item)
    Integer(item.fetch(:price))
  end

  def coupon_discount(coupon)
    raise ArgumentError, "expired coupon" if coupon == :expired

    coupon == :vip ? 10 : 0
  end
end

calculator = DiscountCalculator.new
puts calculator.total([{ price: "25" }, { price: "30" }], :expired)
````

### Raw Dynamic Analysis Output

````text
--- Starting Ruby TracePoint ---
Target file: /tmp/ruby_trace_branch_demo.rb
Tracking file filter: ruby_trace_branch_demo
Local tracking method: total

--- Target script console output ---
55
--- Target script console output ended ---

<target_file>
class DiscountCalculator
  def total(items, coupon)
    subtotal = sum_items(items)
    discount = coupon_discount(coupon)
    subtotal - discount
  rescue ArgumentError
    subtotal
  end

  def sum_items(items)
    items.map { |item| normalize_price(item) }.sum
  end

  def normalize_price(item)
    Integer(item.fetch(:price))
  end

  def coupon_discount(coupon)
    raise ArgumentError, "expired coupon" if coupon == :expired

    coupon == :vip ? 10 : 0
  end
end

calculator = DiscountCalculator.new
puts calculator.total([{ price: "25" }, { price: "30" }], :expired)
</target_file>
* **target_file:** `/tmp/ruby_trace_branch_demo.rb`
* **target_language:** `ruby`
* **file_filter:** `ruby_trace_branch_demo`
* **method_to_trace:** `total`
* **trace_depth:** `12`
* **Filter Level:** Trace `call`, `return`, and `raise` events after the target Ruby method is called.

<trace_log>
```text
0001 CALL   DiscountCalculator#total (/tmp/ruby_trace_branch_demo.rb:2)
0002   CALL   DiscountCalculator#sum_items (/tmp/ruby_trace_branch_demo.rb:10)
0003     CALL   DiscountCalculator#normalize_price (/tmp/ruby_trace_branch_demo.rb:14)
0004     RETURN DiscountCalculator#normalize_price => 25 (/tmp/ruby_trace_branch_demo.rb:16)
0005     CALL   DiscountCalculator#normalize_price (/tmp/ruby_trace_branch_demo.rb:14)
0006     RETURN DiscountCalculator#normalize_price => 30 (/tmp/ruby_trace_branch_demo.rb:16)
0007   RETURN DiscountCalculator#sum_items => 55 (/tmp/ruby_trace_branch_demo.rb:12)
0008   CALL   DiscountCalculator#coupon_discount (/tmp/ruby_trace_branch_demo.rb:18)
0009     RAISE  ArgumentError: expired coupon (/tmp/ruby_trace_branch_demo.rb:19)
0010   RETURN DiscountCalculator#coupon_discount => nil (/tmp/ruby_trace_branch_demo.rb:19)
0011 RETURN DiscountCalculator#total => 55 (/tmp/ruby_trace_branch_demo.rb:8)
```
</trace_log>
````

### Native LLM Summary Output

````text

=================== LLM workflow analyse ==================
# Workflow Execution Analysis Report

## 1. Initial Representation

**Initial Input:** `calculator.total([{ price: "25" }, { price: "30" }], :expired)`

The `total` method receives:
- `items`: Array of 2 hashes `[{price: "25"}, {price: "30"}]`
- `coupon`: Symbol `:expired`

---

## 2. Top-Level Call

```
(1) CALL: DiscountCalculator#total(items=[...], coupon=:expired)
```

---

## 3. Execution Tree

```
(1) Total#total (line 2)
│
├── (2) CALL: DiscountCalculator#sum_items(items) (line 10)
│   │
│   ├── (3) CALL: DiscountCalculator#normalize_price({price: "25"}) (line 14)
│   │   └── (4) RETURN: 25 (line 16)
│   │
│   ├── (5) CALL: DiscountCalculator#normalize_price({price: "30"}) (line 14)
│   │   └── (6) RETURN: 30 (line 16)
│   │
│   └── (7) RETURN: 55 (line 12)  ← [25 + 30]
│
├── (8) CALL: DiscountCalculator#coupon_discount(:expired) (line 18)
│   │
│   ├── (9) RAISE: ArgumentError "expired coupon" (line 19)
│   │   └── Exception escapes coupon_discount without normal return
│   │
│   └── (10) RETURN: nil (line 19) ← Implicitly from rescue/exiting scope
│
└── (11) RETURN: 55 (line 8)  ← [subtotal from (7) - discount(nil) fails → rescue returns subtotal]
```

---

## 4. Final Output

```
Final Output: 55
```

---

## 5. Key Function Analysis

### **Function 1: `DiscountCalculator#total`**
- **Function and Location:** `DiscountCalculator#total` at `/tmp/ruby_trace_branch_demo.rb:2`
- **Functional Boundary:** Calculates final total by computing `subtotal - discount`. Includes an `ArgumentError` rescue block.
- **Role in this Workflow:** Top-level orchestrator. Calls `sum_items` and `coupon_discount`, then attempts subtraction. When `coupon_discount` raises `ArgumentError`, the rescue block catches it and returns `subtotal` directly.

### **Function 2: `DiscountCalculator#sum_items`**
- **Function and Location:** `DiscountCalculator#sum_items` at `/tmp/ruby_trace_branch_demo.rb:10`
- **Functional Boundary:** Sums the normalized prices of all items in the array.
- **Role in this Workflow:** Iterates over items, calls `normalize_price` for each, collects results, and computes the sum. Returns `55` as the subtotal.

### **Function 3: `DiscountCalculator#normalize_price`**
- **Function and Location:** `DiscountCalculator#normalize_price` at `/tmp/ruby_trace_branch_demo.rb:14`
- **Functional Boundary:** Extracts `:price` value from an item hash and converts it to an Integer.
- **Role in this Workflow:** Called twice by `sum_items` — once for each item. Returns `25` and `30` respectively, providing the numeric values needed for the subtotal.

### **Function 4: `DiscountCalculator#coupon_discount`**
- **Function and Location:** `DiscountCalculator#coupon_discount` at `/tmp/ruby_trace_branch_demo.rb:18`
- **Functional Boundary:** Determines discount value based on coupon type. Raises `ArgumentError` if coupon is `:expired`.
- **Role in this Workflow:** Called to calculate the discount. For `:expired` coupon, it raises `ArgumentError` on line 19, triggering the rescue in `total`.

---

## 6. Complete Workflow Summary

The workflow processes a checkout calculation with expired coupon handling:

1. **`total`** begins execution with items `[{price: "25"}, {price: "30"}]` and coupon `:expired`
2. **`sum_items`** processes the items array:
   - Calls `normalize_price` twice, converting string prices to integers (`25`, `30`)
   - Returns subtotal: **55**
3. **`coupon_discount`** attempts to process the `:expired` coupon:
   - Detects `:expired` on line 19
   - Raises `ArgumentError: "expired coupon"`
4. **Exception Handling in `total`:**
   - The `ArgumentError` propagates up from `coupon_discount`
   - Caught by the `rescue ArgumentError` block in `total` (line 6)
   - The rescue block returns `subtotal` (= `55`) instead of performing the subtraction
5. **Final output:** `55` — the subtotal is returned directly, bypassing discount subtraction due to the expired coupon exception.
==============================================================
````

## C/C++

Tool: `run_c_trace`

Notes: Uses GCC/G++ -finstrument-functions to capture function entry and exit events.

### Command

````bash
tools/c_dynamic_analysis_tool/bin/run_c_trace /tmp/c_trace_demo.c '' total 12
````

### Input

````text
#include <stdio.h>

int normalize_price(int cents) {
    return cents / 100;
}

int sum_items(int a, int b) {
    return normalize_price(a) + normalize_price(b);
}

int coupon_discount(int expired) {
    if (expired) {
        return 0;
    }
    return 10;
}

int total(int a, int b, int expired) {
    int subtotal = sum_items(a, b);
    int discount = coupon_discount(expired);
    return subtotal - discount;
}

int main(void) {
    printf("%d\n", total(2500, 3000, 1));
    return 0;
}
````

### Raw Dynamic Analysis Output

````text
--- Starting C/C++ function instrumentation trace ---
Target file: /tmp/c_trace_demo.c
Symbol filter: 
Local tracking function: total

--- Target program console output ---
55
--- Target program console output ended ---

<target_file>
#include <stdio.h>

int normalize_price(int cents) {
    return cents / 100;
}

int sum_items(int a, int b) {
    return normalize_price(a) + normalize_price(b);
}

int coupon_discount(int expired) {
    if (expired) {
        return 0;
    }
    return 10;
}

int total(int a, int b, int expired) {
    int subtotal = sum_items(a, b);
    int discount = coupon_discount(expired);
    return subtotal - discount;
}

int main(void) {
    printf("%d\n", total(2500, 3000, 1));
    return 0;
}
</target_file>
* **target_file:** `/tmp/c_trace_demo.c`
* **target_language:** `c/c++`
* **symbol_filter:** ``
* **function_to_trace:** `total`
* **trace_depth:** `12`
* **Filter Level:** Trace function entry and exit events after the target symbol is entered.

<trace_log>
```text
0001 CALL   total
0002   CALL   sum_items
0003     CALL   normalize_price
0004     RETURN normalize_price
0005     CALL   normalize_price
0006     RETURN normalize_price
0007   RETURN sum_items
0008   CALL   coupon_discount
0009   RETURN coupon_discount
0010 RETURN total
```
</trace_log>
````

### Native LLM Summary Output

````text

=================== LLM workflow analyse ==================
## Execution Workflow Analysis Report

**1. Initial Representation:**
- Input: `total(2500, 3000, 1)` called from `main()`

**2. Top-Level Call:**
```
total(2500, 3000, 1)
```

**3. Execution Tree Diagram:**

```
(1) total(2500, 3000, 1)
    │
    ├── (2) Call: sum_items(2500, 3000)
    │       │
    │       ├── (3) Call: normalize_price(2500)
    │       │       └── Returns: 25 (2500/100)
    │       │
    │       ├── (4) Call: normalize_price(3000)
    │       │       └── Returns: 30 (3000/100)
    │       │
    │       └── (5) Returns: sum_items = 25 + 30 = 55
    │
    ├── (6) Call: coupon_discount(1)  [expired=true]
    │       │
    │       └── (7) Returns: 0 (coupon expired)
    │
    └── (8) Compute: subtotal(55) - discount(0) = 55
    │
    (9) Returns: 55
```

**Final Output:**
```
55
```

**4. Key Function Analysis**

| Function & Location | Functional Boundary | Role in Workflow |
|---------------------|---------------------|------------------|
| **`total`** (`/tmp/c_trace_demo.c:16`) | Orchestrator function that computes final price by coordinating subtotal calculation and discount application | Entry point called from `main()`; manages the overall business logic flow |
| **`sum_items`** (`/tmp/c_trace_demo.c:8`) | Computes sum of two items after normalizing their prices from cents to dollars | Decomposes the subtotal calculation into two independent normalization steps |
| **`normalize_price`** (`/tmp/c_trace_demo.c:4`) | Converts price from cents to dollars by integer division | Provides the fundamental conversion logic used twice by `sum_items` |
| **`coupon_discount`** (`/tmp/c_trace_demo.c:11`) | Determines discount amount based on coupon expiration status | Applies business rule: expired coupon yields no discount; active coupon gives fixed $10 discount |

**5. Workflow Process Summary**

The program calculates the total price of two items ($25.00 + $30.00 = $55.00) with an expired coupon (discount = $0). The execution follows a hierarchical function call pattern:

1. **Main** invokes **total** with item prices (2500¢, 3000¢) and expired coupon flag
2. **Total** calls **sum_items** to compute normalized subtotal:
   - Each price is converted from cents to dollars via **normalize_price**
   - Results (25 + 30 = 55) are summed and returned
3. **Total** calls **coupon_discount** with expired flag = 1 (true):
   - Since coupon is expired, returns 0
4. **Total** computes: subtotal(55) - discount(0) = **55**

The final result `55` is printed to console via `printf`.
==============================================================
````

## JavaScript/TypeScript

Tool: `run_node_trace`

Notes: Uses Node.js inspector CPU profiler. This is sampling-based, so it is best for runtime paths and hotspots rather than exact return values.

### Command

````bash
tools/javascript_dynamic_analysis_tool/bin/run_node_trace /tmp/node_trace_demo.js node_trace_demo total 12
````

### Input

````text
function spin(n) {
  let value = 0;
  for (let i = 0; i < n; i++) {
    value += i % 7;
  }
  return value;
}

function normalizePrice(item) {
  return Number(item.price) + spin(250000);
}

function sumItems(items) {
  return items.map(normalizePrice).reduce((a, b) => a + b, 0);
}

function couponDiscount(coupon) {
  if (coupon === "expired") {
    throw new Error("expired coupon");
  }
  return coupon === "vip" ? 10 : 0;
}

function total(items, coupon) {
  const subtotal = sumItems(items);
  try {
    return subtotal - couponDiscount(coupon);
  } catch (error) {
    return subtotal;
  }
}

console.log(total([{ price: "25" }, { price: "30" }], "expired"));
````

### Raw Dynamic Analysis Output

````text
--- Starting Node.js inspector CPU profile trace ---
Target file: /tmp/node_trace_demo.js
Tracking file filter: node_trace_demo
Local tracking function: total

--- Target script console output ---
1500045
--- Target script console output ended ---

<target_file>
function spin(n) {
  let value = 0;
  for (let i = 0; i < n; i++) {
    value += i % 7;
  }
  return value;
}

function normalizePrice(item) {
  return Number(item.price) + spin(250000);
}

function sumItems(items) {
  return items.map(normalizePrice).reduce((a, b) => a + b, 0);
}

function couponDiscount(coupon) {
  if (coupon === "expired") {
    throw new Error("expired coupon");
  }
  return coupon === "vip" ? 10 : 0;
}

function total(items, coupon) {
  const subtotal = sumItems(items);
  try {
    return subtotal - couponDiscount(coupon);
  } catch (error) {
    return subtotal;
  }
}

console.log(total([{ price: "25" }, { price: "30" }], "expired"));
</target_file>
* **target_file:** `/tmp/node_trace_demo.js`
* **target_language:** `javascript/typescript`
* **file_filter:** `node_trace_demo`
* **function_to_trace:** `total`
* **trace_depth:** `12`
* **Filter Level:** CPU-profiled JavaScript functions after the target function appears in the sampled call tree.

<trace_log>
```text
0001 SAMPLE total hits=1 (file:///tmp/node_trace_demo.js:24:15)
0002   SAMPLE sumItems hits=0 (file:///tmp/node_trace_demo.js:13:18)
0003     SAMPLE normalizePrice hits=0 (file:///tmp/node_trace_demo.js:9:24)
0004       SAMPLE spin hits=3 (file:///tmp/node_trace_demo.js:1:14)
```
</trace_log>
````

### Native LLM Summary Output

````text

=================== LLM workflow analyse ==================
# Execution Workflow Analysis Report

## 1. Initial Representation
**Input:** `total([{ price: "25" }, { price: "30" }], "expired")`
- Items array with 2 objects
- Coupon: "expired" (will trigger error)

## 2. Top-Level Call
`total([{ price: "25" }, { price: "30" }], "expired")`

## 3. Execution Tree

```
(1) total(items=[{price:"25"},{price:"30"}], coupon="expired")
│
├── (2) sumItems(items)
│   │   Calls: map(normalizePrice) then reduce(sum, 0)
│   │
│   ├── (3) normalizePrice({price:"25"})
│   │   │   Process: Number("25") + spin(250000)
│   │   │
│   │   └── (4) spin(250000)
│   │       │   Loop: 0 → 249999
│   │       │   Accumulate: value += (i % 7)
│   │       │   Returns: Calculated integer value
│   │       └── Returns "25 + spin_result"
│   │
│   ├── (5) normalizePrice({price:"30"})
│   │   │   Process: Number("30") + spin(250000)
│   │   │
│   │   └── (6) spin(250000)
│   │       │   Loop: 0 → 249999
│   │       │   Accumulate: value += (i % 7)
│   │       │   Returns: Calculated integer value
│   │       └── Returns "30 + spin_result"
│   │
│   └── (7) reduce(sum)
│       │   Combines: [result_of_normalizePrice1, result_of_normalizePrice2]
│       │   Returns: subtotal = sum of all normalized prices
│       └── Returns subtotal
│
├── (8) couponDiscount("expired")
│   │   Check: coupon === "expired" → true
│   │   Action: throw new Error("expired coupon")
│   └── Returns: Error thrown (not caught here)
│
└── (9) Error Catched by total()
    │   Action: try block fails → enters catch block
    │   Process: return subtotal (ignoring discount)
    └── Returns subtotal
```

## 4. Final Output
```
Final Output: 1500045
```

## 5. Key Function Analysis

### 5.1 Function Details

#### Function 1: `total`
- **Function and Location:** `total` at `/tmp/node_trace_demo.js:24:15`
- **Functional Boundary:** Main orchestrator that calculates final total by combining subtotal with coupon discount
- **Role in this Workflow:** Entry point that:
  1. Calls `sumItems()` to calculate subtotal
  2. Attempts to apply `couponDiscount()` 
  3. Handles potential errors from invalid coupons
  4. Returns either discounted total or raw subtotal

#### Function 2: `sumItems`
- **Function and Location:** `sumItems` at `/tmp/node_trace_demo.js:13:18`
- **Functional Boundary:** Aggregates item prices by mapping prices through normalization and summing results
- **Role in this Workflow:** Processes all items in the array by:
  1. Mapping each item through `normalizePrice()`
  2. Reducing the results using addition
  3. Producing the raw subtotal

#### Function 3: `normalizePrice`
- **Function and Location:** `normalizePrice` at `/tmp/node_trace_demo.js:9:24`
- **Functional Boundary:** Converts string price to number and adds computational overhead
- **Role in this Workflow:** Transforms each item's price by:
  1. Converting string price to numeric value
  2. Adding result of CPU-intensive `spin()` function
  3. Returns the normalized price value

#### Function 4: `spin`
- **Function and Location:** `spin` at `/tmp/node_trace_demo.js:1:14`
- **Functional Boundary:** CPU-intensive loop that simulates work by accumulating modulo results
- **Role in this Workflow:** Performance simulation that:
  1. Loops from 0 to n-1
  2. Accumulates `i % 7` in each iteration
  3. Returns final accumulated value

## 6. Workflow Introduction

The workflow demonstrates a **price calculation system with error handling**. Here's the complete process:

1. **Entry Point:** The `total()` function receives an array of 2 items (prices "25" and "30") and coupon "expired"

2. **Subtotal Calculation:**
   - `total()` calls `sumItems()` which processes each item
   - Each item goes through `normalizePrice()`:
     - Converts string price to number
     - Adds result of CPU-intensive `spin(250000)` operation
   - `spin()` executes 250,000 iterations accumulating modulo 7 values
   - Results are combined via `reduce()` to produce subtotal

3. **Discount Attempt:**
   - `total()` calls `couponDiscount("expired")`
   - Since coupon is "expired", an Error is thrown

4. **Error Handling:**
   - The `try-catch` block in `total()` catches the error
   - Falls back to returning the raw subtotal without discount

5. **Output:** Final result `1500045` represents the total price with error fallback, demonstrating robust error handling in a multi-step calculation pipeline.
==============================================================
````
