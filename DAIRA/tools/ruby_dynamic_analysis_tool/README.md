# Ruby Dynamic Analysis Tool Demo

This document records a standalone test of `run_ruby_trace` and the downstream
LLM workflow summary module already used by SWE-agent.

## Goal

Implement a Ruby dynamic analysis tool with a structure similar to the existing
Python Hunter workflow:

1. Run a small reproduction script.
2. Trace a target method dynamically.
3. Emit `<target_file>` and `<trace_log>` sections.
4. Feed the trace output into the original LLM summary module.
5. Produce a workflow-style execution analysis.

## Tool

```bash
run_ruby_trace <script_path> <file_filter> <method_to_trace> <trace_depth>
```

For this test:

```bash
tools/ruby_dynamic_analysis_tool/bin/run_ruby_trace \
  /tmp/ruby_trace_branch_demo.rb \
  ruby_trace_branch_demo \
  total \
  12
```

## Input

### Ruby Reproduction Script

```ruby
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
```

### Trace Parameters

```text
script_path: /tmp/ruby_trace_branch_demo.rb
file_filter: ruby_trace_branch_demo
method_to_trace: total
trace_depth: 12
```

## Raw Tool Output

The script prints `55`, then the tool emits the target file and trace log.

```text
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
```

## LLM Summary Module

The raw output above was passed to the original SWE-agent summary function:

```python
from sweagent.agent.trace_summary import handle_trace_log

summary = handle_trace_log(trace_output)
```

The test was run with:

```bash
conda run -n sweagent \
  python /tmp/run_ruby_trace_summary.py
```

## LLM Summary Output

```text
=================== LLM workflow analyse ==================
## Execution workflow report

### 1. Initial representation
`calculator.total([{ price: "25" }, { price: "30" }], :expired)`

### 2. Top-level call
`DiscountCalculator#total` (`/tmp/ruby_trace_branch_demo.rb:2`)

### 3. Execution tree

```
(1) CALL DiscountCalculator#total(items=[{price:"25"},{price:"30"}], coupon=:expired)
    │
    ├─ (2) CALL DiscountCalculator#sum_items(items)
    │    │
    │    ├─ (3) CALL normalize_price({price:"25"})
    │    │    └─ (4) RETURN normalize_price => 25
    │    │
    │    ├─ (5) CALL normalize_price({price:"30"})
    │    │    └─ (6) RETURN normalize_price => 30
    │    │
    │    └─ (7) RETURNs sum_items => 55
    │
    ├─ (8) CALL DiscountCalculator#coupon_discount(coupon=:expired)
    │    │
    │    └─ (9) RAISE ArgumentError: "expired coupon" (line 19)
    │         │
    │         └─ (10) RETURN coupon_discount => nil (exception propagated)
    │
    └─ (11) RESCUE block handles the error (line 6-7)
         │
         └─ RETURN subtotal(55) as the final result
```

### 4. Final output
`Final Output: 55`

### 5. Key function analysis

- `DiscountCalculator#total`: orchestrates subtotal calculation, discount lookup, and error recovery.
- `DiscountCalculator#sum_items`: normalizes item prices and computes the subtotal.
- `DiscountCalculator#normalize_price`: converts each price field to an integer.
- `DiscountCalculator#coupon_discount`: validates the coupon and raises on the expired coupon path.

### 6. Workflow summary

The workflow first computes the subtotal, then checks the coupon. The expired coupon raises an
`ArgumentError`, which is handled by `total`; the method safely returns the subtotal `55`.
==============================================================
```

## Summary

The Ruby dynamic analysis module successfully captures:

- The top-level traced method: `DiscountCalculator#total`.
- Nested method calls: `sum_items`, `normalize_price`, and `coupon_discount`.
- Return values from traced methods.
- Runtime exception events through Ruby `TracePoint`.
- The final recovered return value after `rescue ArgumentError`.

The downstream LLM summary module is compatible with this Ruby trace format
because the output follows the same high-level contract as the Python Hunter
tool: a source-code block plus a structured trace log.

## Final Interpretation

The runtime behavior is:

1. `total` receives two prices, `"25"` and `"30"`, and an expired coupon.
2. `sum_items` calls `normalize_price` twice and returns `55`.
3. `coupon_discount` raises `ArgumentError` for the expired coupon.
4. `total` catches that exception in its `rescue ArgumentError` block.
5. The final result is the subtotal, `55`.
