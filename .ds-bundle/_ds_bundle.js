/* @ds-bundle: {"namespace":"Frontend","components":[{"name":"Button","sourcePath":"components/general/Button/Button.jsx"},{"name":"Image","sourcePath":"components/general/Image/Image.jsx"},{"name":"Link","sourcePath":"components/general/Link/Link.jsx"},{"name":"Shimmer","sourcePath":"components/general/Shimmer/Shimmer.jsx"},{"name":"Text","sourcePath":"components/general/Text/Text.jsx"},{"name":"ThemeToggle","sourcePath":"components/general/ThemeToggle/ThemeToggle.jsx"}],"sourceHashes":{"components/general/Button/Button.jsx":"73f77481fb59","components/general/Button/Button.d.ts":"982ca4a701be","components/general/Button/Button.prompt.md":"0ae6fe6b14d7","components/general/Image/Image.jsx":"6af3648b4840","components/general/Image/Image.d.ts":"20f657f341f3","components/general/Image/Image.prompt.md":"f86b1c46baf4","components/general/Link/Link.jsx":"7cf542de2239","components/general/Link/Link.d.ts":"0a7543bb4169","components/general/Link/Link.prompt.md":"6c892e948823","components/general/Shimmer/Shimmer.jsx":"e45188aa7570","components/general/Shimmer/Shimmer.d.ts":"59e2b28b3d24","components/general/Shimmer/Shimmer.prompt.md":"cd8ed5ad846e","components/general/Text/Text.jsx":"94d1baa3179e","components/general/Text/Text.d.ts":"fa9679bf819a","components/general/Text/Text.prompt.md":"1454b3f94cfc","components/general/ThemeToggle/ThemeToggle.jsx":"0cb20dee2eec","components/general/ThemeToggle/ThemeToggle.d.ts":"ba7ffb09aa1a","components/general/ThemeToggle/ThemeToggle.prompt.md":"7d976c4f0cee"},"inlinedExternals":[],"builtBy":"cc-design-sync"} */
var Frontend = (() => {
  // frontend/package.json
  var name = "frontend";
  var version = "0.1.0";
  var private2 = true;
  var scripts = {
    dev: "next dev",
    build: "next build",
    analyze: "ANALYZE=true next build",
    start: "next start",
    lint: "eslint .",
    test: "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:ci": "npm run test:unit",
    "test:unit": "jest --ci --coverage --testPathIgnorePatterns=__tests__/e2e --testPathIgnorePatterns=__tests__/integration --testPathIgnorePatterns=__tests__/helpers --reporters=default --reporters=jest-junit",
    "test:integration": "jest __tests__/integration --ci --reporters=default --reporters=jest-junit",
    "test:e2e": "playwright test",
    doctor: "npx react-doctor@latest"
  };
  var dependencies = {
    "@supabase/supabase-js": "^2.101.0",
    "framer-motion": "^12.34.2",
    "lucide-react": "^0.575.0",
    next: "16.2.10",
    "next-auth": "^4.24.13",
    react: "19.2.0",
    "react-dom": "19.2.0"
  };
  var devDependencies = {
    "@playwright/test": "^1.58.2",
    "@tailwindcss/postcss": "^4",
    "@testing-library/jest-dom": "^6.4.2",
    "@testing-library/react": "^16.3.0",
    "@types/jest": "^29.5.12",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    eslint: "^9",
    "eslint-config-next": "16.2.10",
    jest: "^29.7.0",
    "jest-environment-jsdom": "^29.7.0",
    "jest-junit": "^16.0.0",
    "react-doctor": "^0.7.0",
    tailwindcss: "^4",
    typescript: "^5"
  };
  var package_default = {
    name,
    version,
    private: private2,
    scripts,
    dependencies,
    devDependencies
  };
})();
window.Frontend=Frontend.__dsMainNs?Object.assign({},Frontend,Frontend.__dsMainNs,{__dsMainNs:undefined}):Frontend;
