// Next.js entrypoint of the shared ESLint config, for @rajniti/web.
//
// Today this is the shared base and nothing more: `eslint-config-next` is not
// composed in yet, because @rajniti/web is still a placeholder shell and the
// live Next app in `frontend/` carries its own `eslint-config-next` setup.
// When `frontend/` migrates into apps/web, add `eslint-config-next` to this
// package's peerDependencies and spread its flat config in below.
import base from "./index.mjs";

export default [
  ...base,
];
