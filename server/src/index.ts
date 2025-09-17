import express from 'express';
import cors from 'cors';

// --- Tool Registry and I/O Bridge ---

const toolRegistry = new Map<string, any>();

function register(name: string, implementation: any) {
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
  put: (data: any) => {
    // This is a stub for putting data into a persistent memory/vector store.
    console.log(`[Bridge] memory.put called with data:`, data);
  }
};

register('filesystem', { run: (args: any) => `Simulating filesystem access with args: ${JSON.stringify(args)}` });
register('fetch', { run: (args: any) => `Simulating fetch with args: ${JSON.stringify(args)}` });
register('github-downloader', { run: (args: any) => `Simulating github-downloader with args: ${JSON.stringify(args)}` });
register('command-executor', { run: (args: any) => `Simulating command-executor with args: ${JSON.stringify(args)}` });
register('document-segmentation', { run: (args: any) => [`segment 1`, `segment 2`, `segment 3`] }); // Return array of segments
register('code-reference-indexer', { run: (args: any) => ({ status: 'indexed', indexed_paths: args.paths }) }); // Return object

// --- Express Server Setup ---

const app = express();
const port = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// --- API Endpoints ---

app.post('/mcp/run', (req, res) => {
  const { tool, args } = req.body;
  console.log(`[API] /mcp/run called for tool: ${tool}`);
  if (!toolRegistry.has(tool)) {
    return res.status(404).json({ error: `Tool '${tool}' not found.` });
  }
  try {
    const toolImplementation = toolRegistry.get(tool);
    const result = toolImplementation.run(args);
    res.json({ result });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "An unknown error occurred";
    res.status(500).json({ error: "Tool execution failed", details: errorMessage });
  }
});

app.post('/seg/run', (req, res) => {
  const { docHash } = req.body;
  const docId = docHash || 'default-doc';
  console.log(`[API] /seg/run called for doc: ${docId}`);

  const segTool = toolRegistry.get('document-segmentation');
  const inputText = doc.read(docId);
  const segments = segTool.run({ text: inputText });

  // **Connect to memory.put as per plan**
  memory.put({
      docHash: docId,
      tags: ['seg'],
      segments: segments
  });

  res.json({ segments: segments });
});

app.post('/code-index/run', (req, res) => {
    const { paths } = req.body;
    console.log(`[API] /code-index/run called for paths:`, paths);

    const indexerTool = toolRegistry.get('code-reference-indexer');
    const result = indexerTool.run({ paths });

    // **Connect to memory.put as per plan**
    memory.put({
        type: 'citation',
        scope: 'code-reference',
        references: result
    });

    res.json({ status: "indexing_complete", details: result });
});

app.post('/runlog/put', (req, res) => {
    const logEntry = req.body;
    console.log(`[API] /runlog/put:`, logEntry);
    res.status(201).json({ status: "logged" });
});


app.listen(port, () => {
  console.log(`MCP Server listening on http://localhost:${port}`);
});
