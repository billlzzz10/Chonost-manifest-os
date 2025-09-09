const { execSync } = require('child_process');

/**
 * Get git diff of staged files
 * @returns {string} Git diff output
 */
function getGitDiff() {
  try {
    return execSync('git diff --cached --unified=0', { encoding: 'utf8' });
  } catch (error) {
    console.error('Error getting git diff:', error.message);
    return '';
  }
}

/**
 * Get recent commits for version analysis
 * @param {number} count - Number of recent commits to get
 * @returns {string[]} Array of commit messages
 */
function getRecentCommits(count = 10) {
  try {
    const output = execSync(`git log --oneline -${count}`, { encoding: 'utf8' });
    return output.trim().split('\n').map(line => {
      // Remove commit hash and keep only the message
      const match = line.match(/^[a-f0-9]+\s+(.+)$/);
      return match ? match[1] : line;
    });
  } catch (error) {
    console.error('Error getting recent commits:', error.message);
    return [];
  }
}

/**
 * Get current version from package.json
 * @returns {string} Current version
 */
function getCurrentVersion() {
  try {
    const packageJson = require('../package.json');
    return packageJson.version || '1.0.0';
  } catch (error) {
    console.error('Error getting current version:', error.message);
    return '1.0.0';
  }
}

/**
 * Bump version based on type
 * @param {string} currentVersion - Current version
 * @param {string} type - Version bump type (major, minor, patch)
 * @returns {string} New version
 */
function bumpVersion(currentVersion, type) {
  const parts = currentVersion.split('.');
  const major = parseInt(parts[0] || 0);
  const minor = parseInt(parts[1] || 0);
  const patch = parseInt(parts[2] || 0);

  switch (type) {
    case 'major':
      return `${major + 1}.0.0`;
    case 'minor':
      return `${major}.${minor + 1}.0`;
    case 'patch':
      return `${major}.${minor}.${patch + 1}`;
    default:
      return currentVersion;
  }
}

/**
 * Check if git repository is clean
 * @returns {boolean} True if no changes to commit
 */
function isGitClean() {
  try {
    const output = execSync('git status --porcelain', { encoding: 'utf8' });
    return output.trim() === '';
  } catch (error) {
    console.error('Error checking git status:', error.message);
    return false;
  }
}

/**
 * Get current branch name
 * @returns {string} Current branch name
 */
function getCurrentBranch() {
  try {
    return execSync('git rev-parse --abbrev-ref HEAD', { encoding: 'utf8' }).trim();
  } catch (error) {
    console.error('Error getting current branch:', error.message);
    return 'unknown';
  }
}

module.exports = {
  getGitDiff,
  getRecentCommits,
  getCurrentVersion,
  bumpVersion,
  isGitClean,
  getCurrentBranch
};