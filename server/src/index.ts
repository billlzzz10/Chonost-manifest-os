import express, { Request, Response } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

// --- Type Definitions ---

interface Tool {
  run: (args: Record<string, unknown>) => unknown | Promise<unknown>;
}

// --- Tool Registry and I/O Bridge ---

const toolRegistry = new Map<string, Tool>();

function register(name: string, implementation: Tool) {
  console.log(`Registering tool: ${name}`);
  toolRegistry.set(name, implementation);
}

const doc = {
  read: (docHash: string): string => {
    console.log(`[Bridge] Reading from doc: ${docHash}`);
    return "This is a long document content simulation. ".repeat(1000);
  }
};

const memory = {
  put: (data: Record<string, unknown>) => {
    // This is a stub for putting data into a persistent memory/vector store.
    console.log(`[Bridge] memory.put called with data:`, data);
  }
};

// --- Tool Implementations ---

register('filesystem', { run: (args) => `Simulating filesystem access with args: ${JSON.stringify(args)}` });
register('fetch', { run: (args) => `Simulating fetch with args: ${JSON.stringify(args)}` });
register('github-downloader', { run: (args) => `Simulating github-downloader with args: ${JSON.stringify(args)}` });
register('command-executor', { run: (args) => `Simulating command-executor with args: ${JSON.stringify(args)}` });
register('document-segmentation', { run: () => [`segment 1`, `segment 2`, `segment 3`] });
register('code-reference-indexer', { run: (args) => ({ status: 'indexed', indexed_paths: args.paths }) });

// --- Express Server Setup ---

const app = express();
const port = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// --- API Endpoints ---

app.post('/mcp/run', async (req: Request<{ tool: string, args: Record<string, unknown> }>, res: Response) => {
  try {
    const { tool, args } = req.body;
    const sanitizedTool = typeof tool === 'string' ? tool.replace(/\r?\n/g, "") : String(tool);
    console.log(`[API] /mcp/run called for tool: "${sanitizedTool}"`);
    if (!toolRegistry.has(tool)) {
      return res.status(404).json({ error: `Tool '${tool}' not found.` });
    }
    const toolImplementation = toolRegistry.get(tool)!;
    const result = await toolImplementation.run(args);
    res.json({ result });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "An unknown error occurred";
    res.status(500).json({ error: "Tool execution failed", details: errorMessage });
  }
});

app.post('/seg/run', async (req: Request<{ docHash?: string }>, res: Response) => {
  try {
    const { docHash } = req.body;
    // Use environment variable for default, fallback to a hardcoded value if not set
    const docId = docHash || process.env.DEFAULT_DOC_ID || 'fallback-doc-id';
    console.log(`[API] /seg/run called for doc: ${docId}`);

    const segTool = toolRegistry.get('document-segmentation')!;
    const inputText = doc.read(docId);
    const segments = await segTool.run({ text: inputText });

    memory.put({
        docHash: docId,
        tags: ['seg'],
        segments: segments
    });

    res.json({ segments: segments });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "An unknown error occurred";
    res.status(500).json({ error: "Segmentation failed", details: errorMessage });
  }
});

app.post('/code-index/run', async (req: Request<{ paths: string[] }>, res: Response) => {
  try {
    const { paths } = req.body;
    console.log(`[API] /code-index/run called for paths:`, paths);

    const indexerTool = toolRegistry.get('code-reference-indexer')!;
    const result = await indexerTool.run({ paths });

    memory.put({
        type: 'citation',
        scope: 'code-reference',
        references: result
    });

    res.json({ status: "indexing_complete", details: result });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "An unknown error occurred";
    res.status(500).json({ error: "Indexing failed", details: errorMessage });
  }
});

app.post('/runlog/put', (req: Request, res: Response) => {
  try {
    const logEntry = req.body;
    console.log(`[API] /runlog/put:`, logEntry);
    res.status(201).json({ status: "logged" });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "An unknown error occurred";
    res.status(500).json({ error: "Logging failed", details: errorMessage });
  }
});

app.listen(port, () => {
  console.log(`MCP Server listening on http://localhost:${port}`);
});
