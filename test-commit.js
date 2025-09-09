// Test file for AI-powered commit message hook
// This file is used to test the commit-msg hook functionality

console.log('🧪 Testing AI-powered commit message hook...');

// Test function to simulate git diff
function simulateGitDiff() {
    return `
diff --git a/test-commit.js b/test-commit.js
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/test-commit.js
@@ -0,0 +1,10 @@
+// Test file for AI-powered commit message hook
+// This file is used to test the commit-msg hook functionality
+
+console.log('🧪 Testing AI-powered commit message hook...');
+
+// Test function to simulate git diff
+function simulateGitDiff() {
+    return \`Test diff content\`;
+}
+
+module.exports = { simulateGitDiff };
`;
}

// Export for testing
module.exports = { simulateGitDiff };

console.log('✅ Test file created successfully');
console.log('📝 Now you can test the commit-msg hook by:');
console.log('1. git add test-commit.js');
console.log('2. git commit');
console.log('3. The AI should generate a commit message automatically');