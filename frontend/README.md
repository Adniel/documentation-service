# Documentation Service - Frontend

React frontend for the Documentation Service Platform.

## Quick Start

```bash
# Install dependencies
npm install

# Set up environment
cp .env.example .env

# Start development server
npm run dev
```

The app will be available at http://localhost:5173

## Scripts

```bash
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript checker
npm test             # Run tests (watch mode)
npm run test:run     # Run tests once
npm run test:coverage # Run tests with coverage
```

## Project Structure

```
src/
├── components/       # React components
│   ├── editor/       # TipTap editor components
│   ├── navigation/   # Sidebar, Breadcrumbs
│   ├── search/       # SearchBar
│   └── layout/       # Layout components
├── pages/            # Page components
├── hooks/            # Custom React hooks
├── lib/              # Utilities & API client
├── stores/           # Zustand state stores
├── types/            # TypeScript types
└── test/             # Test utilities
```

## Tech Stack

- React 18 with TypeScript
- TipTap (block editor)
- TanStack Query (data fetching)
- Zustand (state management)
- Tailwind CSS (styling)
- Vitest (testing)

See the main [README](../README.md) for full documentation.
