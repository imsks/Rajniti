# pnpm as the Universal Package Manager

All JavaScript/TypeScript projects in the ecosystem use pnpm, not npm or yarn.

**Context**: Rajniti already uses pnpm. Saransh was initialized with npm. Running mixed package managers causes lockfile drift, inconsistent dependency resolution, and CI cache inefficiencies.

**Decision**: Standardize on pnpm everywhere. Migrate Saransh from npm to pnpm. Sutra already uses pnpm.

**Why pnpm**:
- Faster installs via hard-link content-addressable storage
- Better monorepo support (workspace: protocol)
- Strict dependency isolation prevents phantom dependencies
- Smaller node_modules footprint

**Migration**: Run `rm -rf node_modules package-lock.json && pnpm import && pnpm install` in Saransh.
