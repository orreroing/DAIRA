"""Run a bundled language tracer and summarize its output without SWE-agent."""

import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path

from model import summarize_trace


HERE = Path(__file__).resolve().parent
ADAPTERS = {
    "python": ("python", HERE / "dynamic_analysis_tool/bin/run_hunter_trace"),
    "c": ("python", HERE / "c_dynamic_analysis_tool/bin/run_c_trace"),
    "cpp": ("python", HERE / "c_dynamic_analysis_tool/bin/run_c_trace"),
    "java": ("python", HERE / "java_dynamic_analysis_tool/bin/run_java_trace"),
    "ruby": ("ruby", HERE / "ruby_dynamic_analysis_tool/bin/run_ruby_trace"),
}


def execute_trace(cmd, timeout=180):
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, errors="replace", start_new_session=(os.name == "posix"),
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        # Kill the reproduction and debugger too, not just the tracer wrapper.
        if os.name == "posix":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        else:
            process.kill()
        process.communicate()
        raise RuntimeError(f"Trace command timed out ({timeout} seconds)") from exc
    return subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)


def run(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("language", choices=ADAPTERS)
    parser.add_argument("reproduction", help="Source/script path, or Java reproduction command")
    parser.add_argument("filter", help="File/module/symbol/class filter")
    parser.add_argument("function", help="Function or method to trace")
    parser.add_argument("depth", type=int)
    parser.add_argument("--compile-flags", default="")
    parser.add_argument("--link-flags", default="")
    parser.add_argument("--env-file", type=Path, help="Override skill .env location")
    args = parser.parse_args(argv)
    if args.depth < 1:
        parser.error("depth must be positive")
    if args.language not in {"c", "cpp"} and (args.compile_flags or args.link_flags):
        parser.error("compile/link flags apply only to C/C++")
    runtime, script = ADAPTERS[args.language]
    cmd = [sys.executable if runtime == "python" else runtime,
           str(script), args.reproduction, args.filter, args.function, str(args.depth)]
    if args.compile_flags or args.link_flags:
        cmd += [args.compile_flags, args.link_flags]
    result = execute_trace(cmd)
    if result.returncode:
        raise RuntimeError(f"Trace command failed (exit {result.returncode}):\n{result.stderr[-4000:]}")
    trace = result.stdout
    if len(trace) > 3_000_000:
        raise RuntimeError("Trace is too large; narrow the filter or reduce depth")
    # The bundled source inside <target_file> may itself contain these tags.
    start = trace.rfind("<trace_log>\n")
    end = trace.find("</trace_log>", start) if start >= 0 else -1
    if start < 0 or end < 0 or (start > 0 and trace[start - 1] != "\n"):
        raise RuntimeError("Tracer did not produce a DAIRA trace envelope")
    events = trace[start + len("<trace_log>\n"):end]
    observed = [line for line in events.splitlines()
                if line.strip() and not line.lstrip().startswith(("#", "```"))]
    if not observed:
        raise RuntimeError("No matching trace events; check target and filter")
    if result.stderr.strip():
        trace += "\n<trace_stderr>\n" + result.stderr[-4000:] + "\n</trace_stderr>\n"
    print(summarize_trace(trace, args.language, args.env_file))


if __name__ == "__main__":
    try:
        run()
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"DAIRA trace failed: {exc}", file=sys.stderr)
        sys.exit(1)
