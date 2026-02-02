#!/usr/bin/env python3
"""
Generate ChatGPT Function Definitions from tools.schema.json.
This script converts a `tools.schema.json` file into a list of function
definitions that are compatible with the ChatGPT API.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List


def load_schema(schema_path: str) -> Dict[str, Any]:
    """
    Loads the tools schema from a JSON file.

    Args:
        schema_path (str): The path to the schema file.

    Returns:
        Dict[str, Any]: The loaded schema.
    """
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading schema: {e}")
        sys.exit(1)


def generate_function_definition(
    tool_id: str, schema: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generates a ChatGPT function definition for a single tool.

    Args:
        tool_id (str): The ID of the tool.
        schema (Dict[str, Any]): The tools schema.

    Returns:
        Dict[str, Any]: The ChatGPT function definition.
    """

    # Get tool schema from $defs
    tool_schema = schema.get("$defs", {}).get(tool_id)
    if not tool_schema:
        print(f"Warning: No schema found for {tool_id}")
        return None

    # Extract description from tools.instance.json if available
    description = f"Execute {tool_id} tool"

    # Create function definition
    function_def = {
        "type": "function",
        "function": {
            "name": tool_id,
            "description": description,
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    }

    # Add properties from schema
    if "properties" in tool_schema:
        for prop_name, prop_def in tool_schema["properties"].items():
            if prop_name in [
                "dry_run",
                "timeout_s",
                "job_mode",
                "idempotency_key",
                "cursor",
                "parallel_workers",
                "chunk_size",
                "retry_attempts",
                "retry_delay",
                "progress_callback",
                "memory_limit",
                "cpu_limit",
            ]:
                continue  # Skip common options for ChatGPT

            # Convert schema type to ChatGPT format
            chatgpt_type = "string"
            if prop_def.get("type") == "integer":
                chatgpt_type = "integer"
            elif prop_def.get("type") == "number":
                chatgpt_type = "number"
            elif prop_def.get("type") == "boolean":
                chatgpt_type = "boolean"
            elif prop_def.get("type") == "array":
                chatgpt_type = "array"

            # Add property
            function_def["function"]["parameters"]["properties"][prop_name] = {
                "type": chatgpt_type,
                "description": prop_def.get("description", f"Parameter: {prop_name}"),
            }

            # Add to required if needed
            if tool_schema.get("required") and prop_name in tool_schema["required"]:
                function_def["function"]["parameters"]["required"].append(prop_name)

    return function_def


def generate_all_functions(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generates all function definitions from the tools schema.

    Args:
        schema (Dict[str, Any]): The tools schema.

    Returns:
        List[Dict[str, Any]]: A list of ChatGPT function definitions.
    """
    functions = []

    # Get all tool definitions from $defs
    tool_defs = schema.get("$defs", {})

    for tool_id in tool_defs.keys():
        if tool_id in ["CommonOptions", "Tool"]:
            continue  # Skip meta definitions

        function_def = generate_function_definition(tool_id, schema)
        if function_def:
            functions.append(function_def)

    return functions


def main():
    """
    The main function of the script.

    This function loads the schema, generates the function definitions,
    and then saves the definitions to both a JSON file and a Python file.
    """
    schema_path = "tools.schema.json"

    if not Path(schema_path).exists():
        print(f"Schema file not found: {schema_path}")
        print("Please run this script from the project root directory")
        sys.exit(1)

    # Load schema
    print(f"Loading schema from {schema_path}...")
    schema = load_schema(schema_path)

    # Generate functions
    print("Generating ChatGPT function definitions...")
    functions = generate_all_functions(schema)

    # Output results
    output_file = "chatgpt_functions.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(functions, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(functions)} function definitions")
    print(f"Output saved to: {output_file}")

    # Show sample
    if functions:
        print("\nSample function definition:")
        print(json.dumps(functions[0], indent=2, ensure_ascii=False))

    # Generate Python list for easy copy-paste
    python_output = "chatgpt_functions.py"
    with open(python_output, "w", encoding="utf-8") as f:
        f.write("# ChatGPT Function Definitions\n")
        f.write("# Generated from tools.schema.json\n\n")
        f.write("CHATGPT_FUNCTIONS = ")
        f.write(json.dumps(functions, indent=2, ensure_ascii=False))
        f.write("\n")

    print(f"Python output saved to: {python_output}")


if __name__ == "__main__":
    main()
