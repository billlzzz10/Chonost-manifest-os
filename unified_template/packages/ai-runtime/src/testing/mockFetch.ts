import type { FetchImplementation } from "../types.js";

export function createMockFetch(lines: string[]): FetchImplementation {
  return async () =>
    new Response(lines.join("\n"), {
      headers: {
        "Content-Type": "application/x-ndjson"
      }
    });
}
