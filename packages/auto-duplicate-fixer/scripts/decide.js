
const { program } = require('commander');
const fs = require('fs');
const path = require('path');
const { Project } = require('ts-morph');
const { globSync } = require('glob');

// --- SCORING ---
const SCORE_WEIGHTS = {
  TEST_COVERAGE: 3,
  IMPORT_COUNT: 2,
  TYPE_DEFINITIONS: 5,
  NAMING_CONVENTION: 3,
};

// --- MAIN LOGIC ---
async function decide(reportPath, projectRoot) {
  const report = JSON.parse(fs.readFileSync(reportPath, 'utf-8'));
  const keepRemoveMap = {
    keep: [],
    remove: [],
  };

  const project = new Project({
    // Look for tsconfig in the project root or sub-packages.
    // This may need to be more robust depending on the monorepo structure.
    tsConfigFilePath: path.join(projectRoot, 'tsconfig.json'),
    skipAddingFilesFromTsConfig: true,
  });

  // Ensure all source files are added to the project for analysis
  const tsFiles = globSync(path.join(projectRoot, '**/*.{ts,tsx}'));
  project.addSourceFilesAtPaths(tsFiles);

  for (const duplicate of report.duplicates) {
    const fileA = duplicate.firstFile.name;
    const fileB = duplicate.secondFile.name;

    const scoreA = await scoreFile(fileA, project, projectRoot);
    const scoreB = await scoreFile(fileB, project, projectRoot);

    if (scoreA >= scoreB) {
      keepRemoveMap.keep.push({ file: fileA, score: scoreA });
      keepRemoveMap.remove.push({ file: fileB, score: scoreB });
    } else {
      keepRemoveMap.keep.push({ file: fileB, score: scoreB });
      keepRemoveMap.remove.push({ file: fileA, score: scoreA });
    }
  }

  const outputPath = path.join(process.cwd(), '.keep-remove-map.json');
  fs.writeFileSync(outputPath, JSON.stringify(keepRemoveMap, null, 2));
  console.log(`Keep/remove map saved to ${outputPath}`);
}

async function scoreFile(filePath, project, projectRoot) {
    if (filePath.endsWith('.py')) {
        return scorePythonFile(filePath, projectRoot);
    }
    return scoreTsJsFile(filePath, project, projectRoot);
}

function scorePythonFile(filePath, projectRoot) {
    let score = 0;
    const fileContent = fs.readFileSync(filePath, 'utf-8');

    // 1. Test Coverage (simple version)
    const testFileName = `test_${path.basename(filePath)}`;
    const testFiles = globSync(path.join(projectRoot, '**', testFileName));
    score += testFiles.length * SCORE_WEIGHTS.TEST_COVERAGE;

    // 2. Import Count (simple version)
    const fileNameWithoutExt = path.basename(filePath, '.py');
    const importRegex = new RegExp(`(import ${fileNameWithoutExt}|from ${fileNameWithoutExt} import)`, 'g');
    const allPyFiles = globSync(path.join(projectRoot, '**/*.py'));
    for (const pyFile of allPyFiles) {
        if (pyFile !== filePath) {
            const content = fs.readFileSync(pyFile, 'utf-8');
            if (importRegex.test(content)) {
                score += SCORE_WEIGHTS.IMPORT_COUNT;
            }
        }
    }

    // 4. Naming Convention
    if (filePath.includes('/utils/') || filePath.includes('/common/')) {
        score += SCORE_WEIGHTS.NAMING_CONVENTION;
    }

    return score;
}

async function scoreTsJsFile(filePath, project, projectRoot) {
  let score = 0;

  // 1. Test Coverage
  const testFiles = globSync(
    path.join(projectRoot, '**', `${path.basename(filePath, path.extname(filePath))}.test.{ts,tsx,js,jsx}`)
  );
  score += testFiles.length * SCORE_WEIGHTS.TEST_COVERAGE;

  // 2. Import Count
  const sourceFile = project.getSourceFile(filePath);
  if (sourceFile) {
    const references = sourceFile.getReferencingSourceFiles();
    score += references.length * SCORE_WEIGHTS.IMPORT_COUNT;
  } else {
      console.warn(`Could not find source file in project: ${filePath}`);
  }

  // 3. Type Definitions
  if (filePath.endsWith('.ts') || filePath.endsWith('.tsx')) {
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    if (fileContent.includes('interface ') || fileContent.includes('type ')) {
      score += SCORE_WEIGHTS.TYPE_DEFINITIONS;
    }
  }

  // 4. Naming Convention
  if (filePath.includes('/utils/') || filePath.includes('/services/')) {
    score += SCORE_WEIGHTS.NAMING_CONVENTION;
  }

  return score;
}

// --- CLI ---
program
  .argument('<project>', 'Path to the project root')
  .option('--report <path>', 'Path to the duplicate report JSON', '.duplicate-report.json')
  .action(async (project, options) => {
    try {
      await decide(options.report, project);
    } catch (err) {
      console.error('Error during decision phase:', err);
      process.exit(1);
    }
  });

program.parse(process.argv);
