// Shared base ESLint flat config for Rajniti JS/TS packages.
// App-specific configs (e.g. Next.js) extend this — see next.mjs.
export default [
  {
    ignores: ["**/dist/**", "**/.next/**", "**/node_modules/**", "**/coverage/**"],
  },
  {
    rules: {
      "no-console": ["warn", { allow: ["warn", "error"] }],
      "no-unused-vars": "off",
    },
  },
];
