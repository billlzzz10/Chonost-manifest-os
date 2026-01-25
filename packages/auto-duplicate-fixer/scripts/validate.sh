
#!/bin/bash
set -e

PROJECT_ROOT=${1:-.}
LOG_FILE=".validation-log.json"
RESULTS={}

function run_validation {
  COMMAND=$1
  NAME=$2

  echo "Running $NAME..."
  if eval $COMMAND; then
    echo "$NAME successful."
    RESULTS=$(echo $RESULTS | jq --arg name "$NAME" '. + {($name): "success"}')
  else
    echo "$NAME failed."
    RESULTS=$(echo $RESULTS | jq --arg name "$NAME" '. + {($name): "failed"}')
    echo "$RESULTS" > $LOG_FILE
    git checkout -- .
    exit 1
  fi
}

cd $PROJECT_ROOT

# Install Python dependencies
pip install "fastapi[all]" requests pytest httpx pytest-asyncio openai google-generativeai

# Backend Tests
run_validation "cd apps/backend && PYTHONPATH=. python3 -m pytest" "Backend Tests (pytest)"

# Frontend Lint
run_validation "npm run lint --workspace=@chonost/web" "Frontend Lint"

# TypeCheck (if tsconfig.json exists)
if [ -f "tsconfig.json" ]; then
  run_validation "npx tsc --noEmit" "TypeScript Type Check"
fi

# Build (if build script exists)
if grep -q '"build"' package.json; then
    run_validation "npm run build:web" "NPM Build"
fi

echo "All validation steps passed."
echo "$RESULTS" > $LOG_FILE
exit 0
