
const { program } = require('commander');
const fs = require('fs');
const path = require('path');
const { Project } = require('ts-morph');
const { globSync } = require('glob');

// --- MAIN LOGIC ---
async function refactor(mapPath, projectRoot) {
  const map = JSON.parse(fs.readFileSync(mapPath, 'utf-8'));
  const refactorLog = {
    updatedImports: [],
    deletedFiles: [],
    errors: [],
  };

  const project = new Project({
    tsConfigFilePath: path.join(projectRoot, 'tsconfig.json'),
  });

  const removeToKeepMap = new Map();
  for (let i = 0; i < map.remove.length; i++) {
    removeToKeepMap.set(map.remove[i].file, map.keep[i].file);
  }

  const filesToRemove = Array.from(removeToKeepMap.keys());

  for (const fileToRemove of filesToRemove) {
    const keepFile = removeToKeepMap.get(fileToRemove);
    const sourceFileToRemove = project.getSourceFile(fileToRemove);

    if (sourceFileToRemove) {
      const referencingSourceFiles = sourceFileToRemove.getReferencingSourceFiles();

      for (const referencingSourceFile of referencingSourceFiles) {
        const importDeclarations = referencingSourceFile.getImportDeclarations();

        for (const importDeclaration of importDeclarations) {
          const moduleSpecifier = importDeclaration.getModuleSpecifierValue();
          const absolutePath = path.resolve(path.dirname(referencingSourceFile.getFilePath()), moduleSpecifier);
          const resolvedPath = resolveTsJsImport(absolutePath, projectRoot);

          if (resolvedPath === fileToRemove) {
            const newPath = path.relative(path.dirname(referencingSourceFile.getFilePath()), keepFile);
            importDeclaration.setModuleSpecifier(`./${newPath.replace(/\.tsx?$/, '')}`);
            refactorLog.updatedImports.push({
              file: referencingSourceFile.getFilePath(),
              from: moduleSpecifier,
              to: `./${newPath.replace(/\.tsx?$/, '')}`,
            });
          }
        }
      }
    }
  }

  // Handle Python files separately
  const allPyFiles = globSync(path.join(projectRoot, '**/*.py'));
  for (const pyFile of allPyFiles) {
    let content = fs.readFileSync(pyFile, 'utf-8');
    let changed = false;
    for (const [removeFile, keepFile] of removeToKeepMap.entries()) {
        if(removeFile.endsWith('.py')) {
            const removeModule = pythonPathToModule(removeFile, projectRoot);
            const keepModule = pythonPathToModule(keepFile, projectRoot);

            const regex = new RegExp(`(from ${removeModule} import|import ${removeModule})`, 'g');
            if (regex.test(content)) {
                content = content.replace(regex, (match, p1) => {
                    return p1.startsWith('from') ? `from ${keepModule} import` : `import ${keepModule}`;
                });
                changed = true;
                refactorLog.updatedImports.push({
                    file: pyFile,
                    from: removeModule,
                    to: keepModule
                });
            }
        }
    }
    if(changed) {
        fs.writeFileSync(pyFile, content);
    }
  }


  // Save changes to TS/JS files
  await project.save();

  // Delete the removed files
  for (const fileToRemove of filesToRemove) {
    try {
      if (fs.existsSync(fileToRemove)) {
        fs.unlinkSync(fileToRemove);
        refactorLog.deletedFiles.push(fileToRemove);
      }
    } catch (err) {
      refactorLog.errors.push(`Error deleting file ${fileToRemove}: ${err.message}`);
    }
  }

  const outputPath = path.join(process.cwd(), '.refactor-log.json');
  fs.writeFileSync(outputPath, JSON.stringify(refactorLog, null, 2));
  console.log(`Refactor log saved to ${outputPath}`);
}

function pythonPathToModule(filePath, projectRoot) {
    const relativePath = path.relative(projectRoot, filePath);
    return relativePath.replace(/\.py$/, '').replace(new RegExp(`\\${path.sep}`, 'g'), '.');
}

function resolveTsJsImport(importPath, projectRoot) {
    const extensions = ['.ts', '.tsx', '.js', '.jsx'];
    for (const ext of extensions) {
        if (fs.existsSync(importPath + ext)) {
            return path.resolve(importPath + ext);
        }
    }
    for (const ext of extensions) {
        if (fs.existsSync(path.join(importPath, 'index' + ext))) {
            return path.resolve(path.join(importPath, 'index' + ext));
        }
    }
    return importPath;
}

// --- CLI ---
program
  .argument('<project>', 'Path to the project root')
  .option('--map <path>', 'Path to the keep/remove map', '.keep-remove-map.json')
  .action(async (project, options) => {
    try {
      await refactor(options.map, project);
    } catch (err) {
      console.error('Error during refactor phase:', err);
      process.exit(1);
    }
  });

program.parse(process.argv);
