import { readFile } from "node:fs/promises";
import { argv, stdin, stdout } from "node:process";
import { completeText, streamText } from "./stream.js";
import { completionInputSchema } from "./types.js";

async function main(): Promise<void> {
  try {
    const { data, stream } = await readInput();
    const json = JSON.parse(data);
    const input = completionInputSchema.parse(json);

    if (stream) {
      for await (const delta of streamText(input)) {
        stdout.write(JSON.stringify(delta) + "\n");
      }
      return;
    }

    const result = await completeText(input);
    stdout.write(JSON.stringify(result, null, 2));
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(message);
    process.exitCode = 1;
  }
}

async function readInput(): Promise<{ data: string; stream: boolean }> {
  const args = new Map<string, string>();

  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (!arg?.startsWith("--")) {
      continue;
    }

    const key = arg.slice(2);
    const next = argv[i + 1];
    if (next && !next.startsWith("--")) {
      args.set(key, next);
      i += 1;
    } else {
      args.set(key, "");
    }
  }

  if (args.has("input")) {
    const filePath = args.get("input");
    if (!filePath) {
      throw new Error("--input flag requires a file path");
    }
    const data = await readFile(filePath, "utf8");
    return { data, stream: args.has("stream") };
  }

  if (stdin.isTTY) {
    throw new Error("Provide completion JSON via STDIN or --input <file>");
  }

  const chunks: Buffer[] = [];
  for await (const chunk of stdin) {
    chunks.push(typeof chunk === "string" ? Buffer.from(chunk) : chunk);
  }

  return { data: Buffer.concat(chunks).toString("utf8"), stream: args.has("stream") };
}

void main();
