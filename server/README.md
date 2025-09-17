# MCP Server

This server provides an API for running MCP (Multi-Context Prompting) tools.

## Configuration

The following environment variables can be used for configuration:

- `MCP_TOOLS`: A comma-separated list of tools to enable.
  - Example: `MCP_TOOLS=fs,fetch,ghdl,cmd,seg,codeidx`
- `SEG_THRESHOLD_CHARS`: The character count threshold at which documents should be automatically segmented.
  - Example: `SEG_THRESHOLD_CHARS=8000`

## Running the server

To run the server in development mode:

```bash
pnpm --filter server dev
```
