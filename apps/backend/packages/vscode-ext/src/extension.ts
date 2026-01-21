import * as vscode from "vscode";
import * as fs from "fs";
import * as path from "path";

interface ToolSpec {
  tool_id: string;
  server: string;
  title?: string;
  description?: string;
  parameters?: any;
  output?: any;
}

interface CommonOptions {
  dry_run?: boolean;
  timeout_s?: number;
  job_mode?: "sync" | "async";
  idempotency_key?: string;
  cursor?: string;
}

async function loadTools(ctx: vscode.ExtensionContext): Promise<ToolSpec[]> {
  try {
    const cfg = vscode.workspace.getConfiguration("chonost");
    const schemaPath = cfg.get<string>("toolsSchemaPath")!;
    const fullPath = schemaPath.replace(
      "${workspaceFolder}",
      vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || ""
    );

    if (!fs.existsSync(fullPath)) {
      throw new Error(`Tools schema not found: ${fullPath}`);
    }

    const text = fs.readFileSync(fullPath, "utf-8");
    const json = JSON.parse(text);
    const tools: ToolSpec[] = json.tools || [];

    ctx.workspaceState.update("chonost.tools", tools);
    return tools;
  } catch (error) {
    vscode.window.showErrorMessage(`Failed to load tools: ${error}`);
    return [];
  }
}

async function callOrchestrator(
  server: string,
  tool: string,
  args: any
): Promise<any> {
  try {
    const cfg = vscode.workspace.getConfiguration("chonost");
    const baseUrl = cfg.get<string>("orchestratorUrl")!;

    const response = await fetch(`${baseUrl}/mcp/call`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ server, tool, arguments: args }),
    });

    if (!response.ok) {
      throw new Error(
        `MCP call failed: ${response.status} ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Failed to call orchestrator: ${error}`);
  }
}

async function promptArgs(schema: any): Promise<any> {
  const out: any = {};
  const props = schema?.properties || {};

  // Add common options first
  out.dry_run = await vscode.window
    .showQuickPick(["false", "true"], {
      placeHolder: "Dry run mode",
      ignoreFocusOut: true,
    })
    .then((v) => v === "true");

  out.job_mode = await vscode.window.showQuickPick(["sync", "async"], {
    placeHolder: "Job mode",
    ignoreFocusOut: true,
  });

  // Advanced common options
  const advancedOptions = await vscode.window.showQuickPick(
    ["Basic", "Advanced"],
    {
      placeHolder: "Show advanced options?",
      ignoreFocusOut: true,
    }
  );

  if (advancedOptions === "Advanced") {
    // Timeout
    const timeout = await vscode.window.showInputBox({
      prompt: "Timeout (seconds)",
      placeHolder: "60",
      validateInput: (s) => (isNaN(Number(s)) ? "Must be a number" : undefined),
      ignoreFocusOut: true,
    });
    if (timeout !== undefined) out.timeout_s = Number(timeout);

    // Parallel workers
    const workers = await vscode.window.showInputBox({
      prompt: "Parallel workers",
      placeHolder: "4",
      validateInput: (s) => (isNaN(Number(s)) ? "Must be a number" : undefined),
      ignoreFocusOut: true,
    });
    if (workers !== undefined) out.parallel_workers = Number(workers);

    // Chunk size
    const chunkSize = await vscode.window.showInputBox({
      prompt: "Chunk size",
      placeHolder: "1000",
      validateInput: (s) => (isNaN(Number(s)) ? "Must be a number" : undefined),
      ignoreFocusOut: true,
    });
    if (chunkSize !== undefined) out.chunk_size = Number(chunkSize);

    // Retry attempts
    const retries = await vscode.window.showInputBox({
      prompt: "Retry attempts",
      placeHolder: "3",
      validateInput: (s) => (isNaN(Number(s)) ? "Must be number" : undefined),
      ignoreFocusOut: true,
    });
    if (retries !== undefined) out.retry_attempts = Number(retries);

    // Progress callback
    out.progress_callback = await vscode.window
      .showQuickPick(["false", "true"], {
        placeHolder: "Enable progress callbacks",
        ignoreFocusOut: true,
      })
      .then((v) => v === "true");

    // Memory limit
    const memoryLimit = await vscode.window.showInputBox({
      prompt: "Memory limit (e.g., 1GB, 512MB)",
      placeHolder: "1GB",
      ignoreFocusOut: true,
    });
    if (memoryLimit !== undefined) out.memory_limit = memoryLimit;

    // CPU limit
    const cpuLimit = await vscode.window.showInputBox({
      prompt: "CPU limit (%)",
      placeHolder: "100",
      validateInput: (s) => (isNaN(Number(s)) ? "Must be a number" : undefined),
      ignoreFocusOut: true,
    });
    if (cpuLimit !== undefined) out.cpu_limit = Number(cpuLimit);
  }

  // Prompt for specific parameters
  for (const [key, def] of Object.entries(props)) {
    if (
      key === "dry_run" ||
      key === "job_mode" ||
      key === "timeout_s" ||
      key === "parallel_workers" ||
      key === "chunk_size" ||
      key === "retry_attempts" ||
      key === "retry_delay" ||
      key === "progress_callback" ||
      key === "memory_limit" ||
      key === "cpu_limit"
    )
      continue; // Already handled

    const required = schema.required?.includes(key);
    const defaultValue = def.default;

    if (def.type === "string") {
      const value = await vscode.window.showInputBox({
        prompt: `${key}${required ? " *" : ""}`,
        placeHolder: defaultValue ? `Default: ${defaultValue}` : undefined,
        ignoreFocusOut: true,
      });
      if (value !== undefined) out[key] = value;
      else if (required && defaultValue) out[key] = defaultValue;
    } else if (def.type === "number" || def.type === "integer") {
      const value = await vscode.window.showInputBox({
        prompt: `${key}${required ? " *" : ""}`,
        placeHolder: defaultValue ? `Default: ${defaultValue}` : undefined,
        validateInput: (s) =>
          isNaN(Number(s)) ? "Must be a number" : undefined,
        ignoreFocusOut: true,
      });
      if (value !== undefined) out[key] = Number(value);
      else if (required && defaultValue) out[key] = defaultValue;
    } else if (def.type === "boolean") {
      const value = await vscode.window.showQuickPick(["false", "true"], {
        placeHolder: `${key}${required ? " *" : ""}`,
        ignoreFocusOut: true,
      });
      if (value !== undefined) out[key] = value === "true";
      else if (required && defaultValue) out[key] = defaultValue;
    } else if (def.type === "array") {
      const value = await vscode.window.showInputBox({
        prompt: `${key}${required ? " *" : ""} (comma-separated)`,
        placeHolder: defaultValue
          ? `Default: ${defaultValue.join(", ")}`
          : undefined,
        ignoreFocusOut: true,
      });
      if (value !== undefined) out[key] = value.split(",").map((s) => s.trim());
      else if (required && defaultValue) out[key] = defaultValue;
    }
  }

  return out;
}

async function showResult(result: any, toolId: string) {
  const content = JSON.stringify(result, null, 2);
  const doc = await vscode.workspace.openTextDocument({
    content: `// Result from ${toolId}\n${content}`,
    language: "json",
  });

  await vscode.window.showTextDocument(doc, { preview: true });

  // Show summary in notification
  const summary =
    typeof result === "object" && result.result
      ? `Tool executed successfully`
      : `Tool completed`;

  vscode.window.showInformationMessage(summary);
}

export function activate(context: vscode.ExtensionContext) {
  console.log("Chonost MCP Tools extension is now active!");

  // Command: Run specific tool by ID
  const runCmd = vscode.commands.registerCommand(
    "chonost.tools.run",
    async () => {
      try {
        const tools = await loadTools(context);
        if (tools.length === 0) {
          vscode.window.showErrorMessage("No tools available");
          return;
        }

        const toolId = await vscode.window.showInputBox({
          prompt: "Enter tool ID",
          placeHolder: "e.g., fs.semantic_search, gh.pr_create_smart",
          ignoreFocusOut: true,
        });

        if (!toolId) return;

        const spec = tools.find((t) => t.tool_id === toolId);
        if (!spec) {
          vscode.window.showErrorMessage(`Tool '${toolId}' not found`);
          return;
        }

        const args = await promptArgs(spec.parameters);
        if (!args) return;

        vscode.window.showInformationMessage(`Executing ${toolId}...`);
        const result = await callOrchestrator(spec.server, spec.tool_id, args);

        await showResult(result, toolId);
      } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
      }
    }
  );

  // Command: Pick tool from list and run
  const pickCmd = vscode.commands.registerCommand(
    "chonost.tools.pickAndRun",
    async () => {
      try {
        const tools = await loadTools(context);
        if (tools.length === 0) {
          vscode.window.showErrorMessage("No tools available");
          return;
        }

        const picked = await vscode.window.showQuickPick(
          tools.map((t) => ({
            label: t.title || t.tool_id,
            description: `${t.server} - ${t.description || "No description"}`,
            tool: t,
          })),
          { placeHolder: "Select a tool to run", ignoreFocusOut: true }
        );

        if (!picked) return;

        const args = await promptArgs(picked.tool.parameters);
        if (!args) return;

        vscode.window.showInformationMessage(
          `Executing ${picked.tool.tool_id}...`
        );
        const result = await callOrchestrator(
          picked.tool.server,
          picked.tool.tool_id,
          args
        );

        await showResult(result, picked.tool.tool_id);
      } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
      }
    }
  );

  // Command: List available tools
  const listCmd = vscode.commands.registerCommand(
    "chonost.tools.list",
    async () => {
      try {
        const tools = await loadTools(context);
        if (tools.length === 0) {
          vscode.window.showInformationMessage("No tools available");
          return;
        }

        const content = tools.map((t) => ({
          tool_id: t.tool_id,
          server: t.server,
          title: t.title || t.tool_id,
          description: t.description || "No description",
        }));

        const doc = await vscode.workspace.openTextDocument({
          content: `// Available Chonost MCP Tools\n${JSON.stringify(
            content,
            null,
            2
          )}`,
          language: "json",
        });

        await vscode.window.showTextDocument(doc, { preview: true });
        vscode.window.showInformationMessage(`Found ${tools.length} tools`);
      } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
      }
    }
  );

  context.subscriptions.push(runCmd, pickCmd, listCmd);
}

export function deactivate() {
  console.log("Chonost MCP Tools extension deactivated");
}
