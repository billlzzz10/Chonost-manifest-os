
const { program } = require('commander');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// --- MAIN LOGIC ---
async function deploy(projectRoot, refactorLogPath) {
  const refactorLog = JSON.parse(fs.readFileSync(refactorLogPath, 'utf-8'));
  const deployLog = {
    commitHash: null,
    errors: [],
  };

  try {
    const deletedCount = refactorLog.deletedFiles.length;
    const updatedCount = refactorLog.updatedImports.length;

    const commitMessage = `Auto-fix: Remove duplicates and refactor imports

Files deleted: ${deletedCount}
Imports updated: ${updatedCount}

Automated by auto-duplicate-fixer skill`;

    execSync('git add -A', { cwd: projectRoot });
    execSync(`git commit -m "${commitMessage}"`, { cwd: projectRoot, stdio: 'inherit' });

    const commitHash = execSync('git rev-parse HEAD', { cwd: projectRoot }).toString().trim();
    deployLog.commitHash = commitHash;
    console.log(`Successfully committed changes. Commit hash: ${commitHash}`);

  } catch (err) {
    deployLog.errors.push(`Error during deployment: ${err.message}`);
    console.error('Error during deployment:', err);
  }

  const outputPath = path.join(process.cwd(), '.deploy-log.json');
  fs.writeFileSync(outputPath, JSON.stringify(deployLog, null, 2));
  console.log(`Deploy log saved to ${outputPath}`);
}

// --- CLI ---
program
  .argument('<project>', 'Path to the project root')
  .option('--refactor-log <path>', 'Path to the refactor log', '.refactor-log.json')
  .action(async (project, options) => {
    try {
      await deploy(project, options.refactorLog);
    } catch (err) {
      console.error('Error during deploy phase:', err);
      process.exit(1);
    }
  });

program.parse(process.argv);
