# Rajniti Frontend 🗳️

Beautiful, India-themed landing page for the Rajniti Election Data API built with Next.js 16, TypeScript, and Tailwind CSS.

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Visit http://localhost:3000
```

### Build for Production

```bash
# Build the application
npm run build

# Start production server
npm start
```

## 🌐 Deploy to Netlify

### Option 1: GitHub Integration (Recommended)

1. Push your code to GitHub
2. Go to [Netlify Dashboard](https://app.netlify.com)
3. Click "Add new site" → "Import an existing project"
4. Connect your GitHub repository
5. Configure build settings:
    - **Base directory**: `frontend`
    - **Build command**: `npm run build`
    - **Publish directory**: `.next`
6. Add environment variables (if needed):
    - `NEXT_PUBLIC_API_URL`: Your backend API URL
7. Click "Deploy site"

### Option 2: Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
netlify deploy --prod
```

### Option 3: Drag & Drop

1. Build locally: `npm run build`
2. Go to [Netlify Drop](https://app.netlify.com/drop)
3. Drag the `.next` folder

## ⚙️ Configuration

### Environment Variables

Create `.env.local` for local development:

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8080
```

For Netlify deployment, set environment variables in:
**Site Settings → Environment Variables**

### Backend Integration

If you have a backend API, update `netlify.toml`:

```toml
[[redirects]]
  from = "/api/*"
  to = "https://your-backend-url.run.app/api/:splat"
  status = 200
  force = false
```

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── dashboard/         # Dashboard page
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── globals.css        # Global styles
├── components/            # React components
│   └── PreambleSection.tsx
├── public/               # Static assets
├── next.config.ts        # Next.js configuration
├── netlify.toml          # Netlify deployment config
├── package.json          # Dependencies
└── tsconfig.json         # TypeScript config
```

## 🎨 Features

-   ⚡ Next.js 16 with App Router
-   🎨 Tailwind CSS 4
-   📱 Fully Responsive Design
-   🇮🇳 India-themed Color Scheme (Orange, White, Green)
-   🚀 Optimized for Netlify Deployment
-   🔒 Security Headers Configured
-   ⚡ Static Asset Caching
-   🌐 API Proxy Support

## 🛠️ Tech Stack

-   **Framework**: Next.js 16
-   **Language**: TypeScript
-   **Styling**: Tailwind CSS 4
-   **Deployment**: Netlify
-   **Package Manager**: npm

## 📦 Dependencies

```json
{
    "dependencies": {
        "react": "19.2.0",
        "react-dom": "19.2.0",
        "next": "16.0.1"
    },
    "devDependencies": {
        "typescript": "^5",
        "@types/node": "^20",
        "@types/react": "^19",
        "@types/react-dom": "^19",
        "@tailwindcss/postcss": "^4",
        "tailwindcss": "^4",
        "eslint": "^9",
        "eslint-config-next": "16.0.1"
    }
}
```

## 🔍 Available Scripts

```bash
# Development
npm run dev          # Start dev server on http://localhost:3000

# Production
npm run build        # Build for production
npm start           # Start production server

# Linting
npm run lint        # Run ESLint
```

## 🌟 Netlify Configuration

The `netlify.toml` file includes:

-   ✅ Next.js plugin for optimal performance
-   ✅ Security headers (CSP, XSS, Frame protection)
-   ✅ Static asset caching
-   ✅ API proxy support (optional)
-   ✅ Node.js 20 environment

## 🐛 Troubleshooting

### Build Fails on Netlify

1. Check Node.js version in `netlify.toml` (should be 20)
2. Verify all dependencies are in `package.json`
3. Check build logs in Netlify Dashboard

### API Calls Not Working

1. Verify `NEXT_PUBLIC_API_URL` is set in Netlify environment variables
2. Check CORS settings on backend
3. Verify API proxy in `netlify.toml` is configured correctly

### Styling Issues

1. Clear `.next` cache: `rm -rf .next`
2. Rebuild: `npm run build`
3. Check Tailwind CSS configuration

## 📚 Resources

-   [Next.js Documentation](https://nextjs.org/docs)
-   [Netlify Documentation](https://docs.netlify.com)
-   [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## 🤝 Contributing

See the main [README.md](../readme.md) for contribution guidelines.

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details.

---

**Built with ❤️ for 🇮🇳 Indian Democracy**
