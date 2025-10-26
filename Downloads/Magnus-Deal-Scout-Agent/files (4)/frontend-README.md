# Deal Scout - Frontend

A modern Next.js 14 application for aggregating and monitoring marketplace listings from eBay, Facebook Marketplace, Gumtree, and Craigslist.

## 🚀 Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS + shadcn/ui
- **State Management:** Zustand
- **Data Fetching:** React Query (TanStack Query)
- **HTTP Client:** Axios
- **Forms:** React Hook Form + Zod
- **Icons:** Lucide React
- **Notifications:** Sonner

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                          # Next.js 14 App Router
│   │   ├── (auth)/                   # Authentication pages
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (dashboard)/              # Protected dashboard routes
│   │   │   ├── dashboard/            # Main dashboard
│   │   │   ├── searches/             # Search management
│   │   │   │   ├── new/              # Create search
│   │   │   │   └── [id]/             # Search detail
│   │   │   └── listings/             # Listing views
│   │   │       └── [id]/             # Listing detail
│   │   ├── layout.tsx                # Root layout
│   │   ├── page.tsx                  # Home (redirects to dashboard)
│   │   ├── providers.tsx             # React Query provider
│   │   └── globals.css               # Global styles
│   ├── components/
│   │   ├── ui/                       # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── select.tsx
│   │   │   └── ...
│   │   ├── layout/                   # Layout components
│   │   ├── searches/                 # Search-specific components
│   │   └── listings/                 # Listing-specific components
│   └── lib/
│       ├── api/                      # API client & services
│       │   ├── client.ts             # Axios instance
│       │   ├── auth.ts               # Auth API
│       │   ├── searches.ts           # Searches API
│       │   ├── listings.ts           # Listings API
│       │   └── index.ts              # Exports
│       ├── hooks/                    # React Query hooks
│       │   ├── useAuth.ts
│       │   ├── useSearches.ts
│       │   ├── useListings.ts
│       │   └── useDashboard.ts
│       ├── stores/                   # Zustand stores
│       │   └── useStore.ts
│       ├── types/                    # TypeScript types
│       │   └── index.ts
│       └── utils/                    # Utility functions
│           └── index.ts
├── public/                           # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── README.md
```

## 🛠️ Setup Instructions

### Prerequisites

- Node.js 18.17.0 or higher
- npm 9.0.0 or higher
- Backend API running (see backend README)

### Installation

1. **Install dependencies:**

```bash
npm install
```

2. **Environment Setup:**

Create a `.env.local` file in the root directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Authentication
NEXT_PUBLIC_AUTH_TOKEN_KEY=deal-scout-auth-token
```

3. **Run development server:**

```bash
npm run dev
```

The app will be available at [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
npm start
```

## 📱 Features

### ✅ Implemented

- **Authentication**
  - User registration and login
  - JWT token management
  - Protected routes

- **Dashboard**
  - Real-time statistics
  - Recent searches and listings
  - Quick actions

- **Search Management**
  - Create/edit/delete searches
  - Multi-marketplace selection
  - Location and price filtering
  - Custom check intervals
  - Pause/resume searches

- **Listing Discovery**
  - Browse all listings
  - Filter and sort options
  - Save/bookmark listings
  - Marketplace badges
  - Direct links to original listings

- **UI/UX**
  - Responsive design
  - Loading skeletons
  - Toast notifications
  - Error handling
  - Dark mode support (system preference)

## 🎨 Design System

The application uses shadcn/ui components with a custom theme. Key design tokens:

- **Colors:** Primary (blue), Secondary (gray), Destructive (red)
- **Typography:** Inter font family
- **Spacing:** Tailwind default scale
- **Radius:** 0.5rem default border radius

## 🔧 API Integration

The frontend communicates with the FastAPI backend through a centralized API client. All API calls are wrapped in React Query hooks for:

- Automatic caching
- Background refetching
- Optimistic updates
- Error handling
- Loading states

### Example Usage

```typescript
// Fetching searches
const { data, isLoading, error } = useSearches({ status: 'active' });

// Creating a search
const createSearch = useCreateSearch();
createSearch.mutate(formData);

// Saving a listing
const saveListing = useSaveListing();
saveListing.mutate(listingId);
```

## 🧪 Development

### Code Quality

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format
```

### Adding New Components

1. Create component in appropriate directory
2. Export from index file if needed
3. Add types in `src/lib/types/index.ts`
4. Create API service in `src/lib/api/` if needed
5. Create React Query hook in `src/lib/hooks/` if needed

## 📦 Key Dependencies

### Production
- `next`: ^14.2.0 - React framework
- `react-query`: ^5.28.0 - Server state management
- `zustand`: ^4.5.2 - Client state management
- `axios`: ^1.6.8 - HTTP client
- `tailwindcss`: ^3.4.3 - Styling
- `sonner`: ^1.4.41 - Toast notifications
- `lucide-react`: ^0.363.0 - Icons

### Development
- `typescript`: ^5.4.0
- `eslint`: ^8.57.0
- `prettier`: ^3.2.5

## 🚀 Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

### Docker

```bash
docker build -t deal-scout-frontend .
docker run -p 3000:3000 deal-scout-frontend
```

## 📝 File Organization Guide

When uploading to GitHub, maintain this structure:

```
frontend/
├── .gitignore              → Use frontend-gitignore.txt content
├── .env.example            → Use frontend-env.example
├── package.json            → Use frontend-package.json
├── tsconfig.json           → Use frontend-tsconfig.json
├── next.config.js          → Use frontend-next.config.js
├── tailwind.config.ts      → Use frontend-tailwind.config.ts
├── postcss.config.js       → Use frontend-postcss.config.js
├── .eslintrc.json          → Use frontend-eslintrc.json
└── src/
    ├── app/
    │   ├── globals.css                    → frontend-src-app-globals.css
    │   ├── layout.tsx                     → From frontend-src-app-layout-and-providers.tsx
    │   ├── page.tsx                       → From frontend-src-app-layout-and-providers.tsx
    │   ├── providers.tsx                  → From frontend-src-app-layout-and-providers.tsx
    │   ├── (auth)/
    │   │   ├── login/page.tsx            → From frontend-src-app-auth-pages.tsx (login section)
    │   │   └── register/page.tsx          → From frontend-src-app-auth-pages.tsx (register section)
    │   └── (dashboard)/
    │       ├── layout.tsx                 → frontend-src-app-dashboard-layout.tsx
    │       ├── dashboard/page.tsx         → frontend-src-app-dashboard-page.tsx
    │       ├── searches/
    │       │   ├── page.tsx               → frontend-src-app-searches-page.tsx
    │       │   └── new/page.tsx           → frontend-src-app-searches-new-page.tsx
    │       └── listings/
    │           └── page.tsx               → frontend-src-app-listings-page.tsx
    ├── components/
    │   └── ui/
    │       ├── button.tsx                 → frontend-src-components-ui-button.tsx
    │       ├── input.tsx                  → From frontend-src-components-ui-combined-1.tsx
    │       ├── label.tsx                  → From frontend-src-components-ui-combined-1.tsx
    │       ├── card.tsx                   → From frontend-src-components-ui-combined-1.tsx
    │       ├── badge.tsx                  → From frontend-src-components-ui-combined-2.tsx
    │       ├── select.tsx                 → From frontend-src-components-ui-combined-2.tsx
    │       └── skeleton.tsx               → From frontend-src-components-ui-combined-2.tsx
    └── lib/
        ├── api/
        │   ├── client.ts                  → frontend-src-lib-api-client.ts
        │   ├── auth.ts                    → frontend-src-lib-api-auth.ts
        │   ├── searches.ts                → frontend-src-lib-api-searches.ts
        │   ├── listings.ts                → frontend-src-lib-api-listings.ts
        │   └── index.ts                   → frontend-src-lib-api-index.ts
        ├── hooks/
        │   ├── useAuth.ts                 → frontend-src-lib-hooks-useAuth.ts
        │   ├── useSearches.ts             → frontend-src-lib-hooks-useSearches.ts
        │   ├── useListings.ts             → frontend-src-lib-hooks-useListings.ts
        │   └── useDashboard.ts            → frontend-src-lib-hooks-useDashboard.ts
        ├── stores/
        │   └── useStore.ts                → frontend-src-lib-stores-useStore.ts
        ├── types/
        │   └── index.ts                   → frontend-src-lib-types-index.ts
        └── utils/
            └── index.ts                   → frontend-src-lib-utils-index.ts
```

## 🤝 Contributing

1. Create a feature branch
2. Make changes
3. Add tests if applicable
4. Submit a pull request

## 📄 License

MIT

## 🆘 Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: See `/docs` folder
- API Docs: See backend README

---

**Built with ❤️ using Next.js 14 and TypeScript**
