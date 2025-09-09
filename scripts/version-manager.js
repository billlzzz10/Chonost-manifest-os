const AICommitManager = require('./ai-commit');
const { getCurrentVersion, bumpVersion, getRecentCommits, getCurrentBranch } = require('./git-utils');

class VersionManager {
  constructor() {
    this.aiManager = new AICommitManager('version');
  }

  /**
   * Create a new release with version bump
   * @returns {Promise<Object>} Release information
   */
  async createRelease() {
    try {
      console.log('🚀 Starting version management process...');
      
      // Get current branch
      const branch = getCurrentBranch();
      console.log(`📍 Current branch: ${branch}`);
      
      // Only create releases on main/master branch
      if (branch !== 'main' && branch !== 'master') {
        console.log('⚠️  Skipping release creation (not on main/master branch)');
        return null;
      }
      
      // Get recent commits
      const commits = getRecentCommits(10);
      console.log(`📝 Found ${commits.length} recent commits`);
      
      if (commits.length === 0) {
        throw new Error('No commits found to analyze');
      }
      
      // Determine version bump type
      console.log('🔍 Analyzing commits for version bump...');
      const versionType = await this.aiManager.determineVersionBump(commits);
      console.log(`📦 Version bump type: ${versionType}`);
      
      // Get current version and bump it
      const currentVersion = getCurrentVersion();
      const newVersion = bumpVersion(currentVersion, versionType);
      console.log(`🔄 Version bump: ${currentVersion} → ${newVersion}`);
      
      // Generate release notes
      console.log('📋 Generating release notes...');
      const releaseNotes = await this.aiManager.generateReleaseNotes(commits);
      
      return {
        version: newVersion,
        currentVersion,
        versionType,
        commits,
        releaseNotes,
        branch,
        timestamp: new Date().toISOString()
      };
      
    } catch (error) {
      console.error('❌ Error creating release:', error.message);
      throw error;
    }
  }

  /**
   * Create git tag for the release
   * @param {string} version - Version number
   * @param {string} message - Tag message
   * @returns {Promise<void>}
   */
  async createTag(version, message) {
    try {
      console.log(`🏷️  Creating tag v${version}...`);
      
      // Configure git user for tag creation
      const { execSync } = require('child_process');
      
      execSync('git config --local user.email "action@github.com"', { stdio: 'pipe' });
      execSync('git config --local user.name "GitHub Action"', { stdio: 'pipe' });
      
      // Create tag
      execSync(`git tag -a "v${version}" -m "${message}"`, { stdio: 'pipe' });
      
      console.log(`✅ Tag v${version} created successfully`);
      
    } catch (error) {
      console.error('❌ Error creating tag:', error.message);
      throw error;
    }
  }

  /**
   * Push tag to remote repository
   * @param {string} version - Version number
   * @returns {Promise<void>}
   */
  async pushTag(version) {
    try {
      console.log(`📤 Pushing tag v${version} to remote...`);
      
      const { execSync } = require('child_process');
      execSync(`git push origin "v${version}"`, { stdio: 'pipe' });
      
      console.log(`✅ Tag v${version} pushed successfully`);
      
    } catch (error) {
      console.error('❌ Error pushing tag:', error.message);
      throw error;
    }
  }

  /**
   * Generate changelog from commits
   * @param {string[]} commits - Array of commit messages
   * @returns {Promise<string>} Changelog content
   */
  async generateChangelog(commits) {
    try {
      console.log('📚 Generating changelog...');
      
      const prompt = `Generate a comprehensive changelog in Thai language for these commits:

${commits.map((commit, index) => `${index + 1}. ${commit}`).join('\n')}

Requirements:
- Write in Thai language
- Group changes by category (features, bug fixes, improvements, etc.)
- Use clear section headers
- Include version number placeholder [VERSION]
- Keep it professional but user-friendly
- Maximum 300 words`;

      const systemPrompt = `You are a technical writer who creates professional changelogs.
You write in Thai language and can organize technical information clearly.
You create changelogs that are informative and easy to understand for end users.`;

      return await this.aiManager.generateWithFallback(prompt, systemPrompt);
      
    } catch (error) {
      console.error('❌ Error generating changelog:', error.message);
      throw error;
    }
  }
}

// Export for use in other modules
module.exports = VersionManager;

// CLI usage
if (require.main === module) {
  const versionManager = new VersionManager();
  
  async function main() {
    try {
      const action = process.argv[2];
      
      switch (action) {
        case 'create':
          const release = await versionManager.createRelease();
          if (release) {
            console.log('\n🎉 Release Information:');
            console.log(`Version: ${release.version}`);
            console.log(`Type: ${release.versionType}`);
            console.log(`Branch: ${release.branch}`);
            console.log('\n📝 Release Notes:');
            console.log(release.releaseNotes);
          }
          break;
          
        case 'tag':
          const version = process.argv[3] || '1.0.0';
          const message = process.argv[4] || `Release v${version}`;
          await versionManager.createTag(version, message);
          break;
          
        case 'push':
          const tagVersion = process.argv[3] || '1.0.0';
          await versionManager.pushTag(tagVersion);
          break;
          
        case 'changelog':
          const commits = getRecentCommits(10);
          const changelog = await versionManager.generateChangelog(commits);
          console.log('📚 Changelog:');
          console.log(changelog);
          break;
          
        default:
          console.log('Usage:');
          console.log('  node scripts/version-manager.js create    # Create new release');
          console.log('  node scripts/version-manager.js tag [version] [message]  # Create git tag');
          console.log('  node scripts/version-manager.js push [version]          # Push tag to remote');
          console.log('  node scripts/version-manager.js changelog              # Generate changelog');
      }
    } catch (error) {
      console.error('❌ Error:', error.message);
      process.exit(1);
    }
  }
  
  main();
}