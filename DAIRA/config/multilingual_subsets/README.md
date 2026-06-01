# SWE-bench Multilingual Supported-Language Subsets

Dataset: `swe-bench/SWE-Bench_Multilingual`
Split: `test`
Total rows: `300`

## Selected Instances

### ruby

- `faker-ruby__faker-2705` (faker-ruby/faker)
- `faker-ruby__faker-2970` (faker-ruby/faker)
- `fastlane__fastlane-19207` (fastlane/fastlane)
- `fastlane__fastlane-19304` (fastlane/fastlane)
- `fastlane__fastlane-19765` (fastlane/fastlane)
- `fastlane__fastlane-20642` (fastlane/fastlane)
- `fastlane__fastlane-20958` (fastlane/fastlane)
- `fastlane__fastlane-20975` (fastlane/fastlane)
- `fastlane__fastlane-21857` (fastlane/fastlane)
- `fluent__fluentd-3328` (fluent/fluentd)
- `fluent__fluentd-3466` (fluent/fluentd)
- `fluent__fluentd-3608` (fluent/fluentd)
- `fluent__fluentd-3616` (fluent/fluentd)
- `fluent__fluentd-3631` (fluent/fluentd)
- `fluent__fluentd-3640` (fluent/fluentd)
- `fluent__fluentd-3641` (fluent/fluentd)
- `fluent__fluentd-3917` (fluent/fluentd)

### c_cpp

- `fmtlib__fmt-1683` (fmtlib/fmt)
- `fmtlib__fmt-2310` (fmtlib/fmt)
- `fmtlib__fmt-2317` (fmtlib/fmt)
- `fmtlib__fmt-2457` (fmtlib/fmt)
- `fmtlib__fmt-3158` (fmtlib/fmt)
- `fmtlib__fmt-3248` (fmtlib/fmt)
- `fmtlib__fmt-3272` (fmtlib/fmt)
- `fmtlib__fmt-3729` (fmtlib/fmt)
- `fmtlib__fmt-3750` (fmtlib/fmt)
- `fmtlib__fmt-3863` (fmtlib/fmt)
- `fmtlib__fmt-3901` (fmtlib/fmt)
- `jqlang__jq-2235` (jqlang/jq)
- `jqlang__jq-2598` (jqlang/jq)
- `jqlang__jq-2650` (jqlang/jq)
- `jqlang__jq-2658` (jqlang/jq)
- `jqlang__jq-2681` (jqlang/jq)
- `jqlang__jq-2728` (jqlang/jq)

### java

- `apache__druid-13704` (apache/druid)
- `apache__druid-14092` (apache/druid)
- `apache__druid-14136` (apache/druid)
- `apache__druid-15402` (apache/druid)
- `apache__druid-16875` (apache/druid)
- `apache__lucene-11760` (apache/lucene)
- `apache__lucene-12022` (apache/lucene)
- `apache__lucene-12196` (apache/lucene)
- `apache__lucene-12212` (apache/lucene)
- `apache__lucene-12626` (apache/lucene)
- `apache__lucene-13170` (apache/lucene)
- `apache__lucene-13301` (apache/lucene)
- `apache__lucene-13494` (apache/lucene)
- `apache__lucene-13704` (apache/lucene)
- `google__gson-1014` (google/gson)
- `google__gson-1093` (google/gson)

## Output Files

- Combined: `config/multilingual_subsets/swebench_multilingual_supported_50.yaml`
- ruby: `config/multilingual_subsets/swebench_multilingual_ruby_17.yaml`
- c_cpp: `config/multilingual_subsets/swebench_multilingual_c_cpp_17.yaml`
- java: `config/multilingual_subsets/swebench_multilingual_java_16.yaml`

## Example Commands

Run each language subset with its matching dynamic-analysis config:

```bash
sweagent run-batch --num_workers=1 \
  --instances.type file --instances.path config/multilingual_subsets/swebench_multilingual_ruby_17.yaml \
  --config config/context_retrieval_ruby.yaml \
  --agent.model.name deepseek/deepseek-chat

sweagent run-batch --num_workers=1 \
  --instances.type file --instances.path config/multilingual_subsets/swebench_multilingual_c_cpp_17.yaml \
  --config config/context_retrieval_c.yaml \
  --agent.model.name deepseek/deepseek-chat

sweagent run-batch --num_workers=1 \
  --instances.type file --instances.path config/multilingual_subsets/swebench_multilingual_java_16.yaml \
  --config config/context_retrieval_java.yaml \
  --agent.model.name deepseek/deepseek-chat
```

The combined YAML is useful for bookkeeping, but per-language runs are recommended because each language uses a different dynamic-analysis tool.
