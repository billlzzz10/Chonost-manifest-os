import { Command } from 'commander';
import chalk from 'chalk';
import { createAgent, type AgentMode } from '@unified/agent-core';

const program = new Command();

program
  .name('agent')
  .description('Unified agent CLI (architect → coder → debugger)')
  .argument('<mode>', 'Mode to run (architect|coder|debugger)')
  .argument('[task...]', 'Task description')
  .option('-m, --model <model>', 'Model id', process.env.OLLAMA_MODEL ?? 'qwen2.5-coder')
  .option('-t, --temperature <temperature>', 'Sampling temperature', (value) => Number(value), 0)
  .action(async (mode: string, taskParts: string[], options) => {
    const task = taskParts.join(' ') || 'Summarise latest manuscript updates';
    const agent = createAgent({ model: options.model, temperature: options.temperature });

    agent.on('agent:plan', (plan) => {
      console.log(chalk.cyan('\nPlan:'));
      for (const [index, step] of plan.steps.entries()) {
        console.log(chalk.cyan(${index + 1}. ));
      }
    });

    agent.on('agent:step-end', (result) => {
      console.log(chalk.green(\n✔ Step  complete));
    });

    agent.on('agent:issue', (issue) => {
      console.log(chalk.yellow(⚠ Issue:  []));
      if (issue.suggestion) {
        console.log(chalk.gray(Suggestion: ));
      }
    });

    agent.on('agent:complete', ({ summary }) => {
      console.log(chalk.magenta(\n));
    });

    agent.on('agent:error', (error) => {
      console.error(chalk.red(Error: ));
      if (error.cause) {
        console.error(error.cause);
      }
      process.exitCode = 1;
    });

    await agent.run(mode as AgentMode, { task });
  });

program.parseAsync();

