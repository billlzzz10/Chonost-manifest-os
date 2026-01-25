
const { program } = require('commander');
const { jscpd } = require('jscpd');
const fs = require('fs');
const path = require('path');

program
  .argument('<project>', 'Path to the project root')
  .option('--format <format>', 'Output format', 'json')
  .option('--min-tokens <tokens>', 'Minimum tokens to be considered a duplicate', '50')
  .action(async (project, options) => {
    try {
      console.log(`Scanning project at: ${project}`);

      const ignorePatterns = [
        '**/node_modules/**',
        '**/dist/**',
        '**/build/**',
        '**/coverage/**',
        '**/.git/**',
      ].join(',');

      const jscpdArgs = [
        'node',
        'jscpd',
        project,
        '--min-tokens', options.minTokens,
        '--reporters', options.format === 'json' ? 'json' : 'console',
        '--output', '.jscpd',
        '--pattern', '**/*.{ts,tsx,js,jsx,py}',
        '--ignore', ignorePatterns,
        '--absolute',
      ];

      await jscpd(jscpdArgs);

      if (options.format === 'json') {
        const reportPath = path.join(process.cwd(), '.duplicate-report.json');
        const generatedReportPath = path.join(process.cwd(), '.jscpd', 'jscpd-report.json');

        if (fs.existsSync(generatedReportPath)) {
            const reportContent = fs.readFileSync(generatedReportPath, 'utf-8');
            fs.writeFileSync(reportPath, reportContent);
            console.log(`Duplicate report saved to ${reportPath}`);
        } else {
            console.log('No duplicates found or jscpd did not generate a report.');
            const emptyReport = {
                "duplicates": [],
                "statistics": {}
            };
            fs.writeFileSync(reportPath, JSON.stringify(emptyReport, null, 2));
            console.log(`Empty duplicate report saved to ${reportPath}`);
        }

        // Clean up the jscpd output directory
        if (fs.existsSync(path.join(process.cwd(), '.jscpd'))) {
            fs.rmSync(path.join(process.cwd(), '.jscpd'), { recursive: true, force: true });
        }
      }

    } catch (err) {
      console.error('Error during duplicate detection:', err);
      process.exit(1);
    }
  });

program.parse(process.argv);
