/** Saransh frontend URL — env-driven so the destination can change without a redeploy. */
export const SARANSH_URL =
  process.env.NEXT_PUBLIC_SARANSH_URL || "https://saransh-app.vercel.app";
