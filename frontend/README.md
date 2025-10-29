# Deal Scout Frontend

Modern Next.js 14 frontend application for the Deal Scout marketplace search agent.

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Form Management**: React Hook Form + Zod
- **Icons**: Lucide React
- **Charts**: Recharts

## Features

- 🔐 JWT-based authentication with automatic token refresh
- 📊 Real-time dashboard with statistics
- 🔍 Search management (create, pause, delete)
- 📋 Listings browser with save and archive functionality
- 🎨 Modern, responsive UI built with Tailwind CSS
- 📱 Mobile-friendly design
- 🔄 Automatic API error handling and retry logic

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Backend API running (see `../backend/README.md`)

### Installation

1. Install dependencies:

```bash
npm install
# or
yarn install
# or
pnpm install
```

2. Create environment file:

```bash
cp .env.example .env
```

3. Configure environment variables in `.env`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1
```

### Development

Run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

Create a production build:

```bash
npm run build
npm start
```

### Type Checking

Run TypeScript type checking:

```bash
npm run type-check
```

### Linting

Run ESLint:

```bash
npm run lint
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── auth/              # Authentication pages
│   │   ├── dashboard/         # Dashboard page
│   │   ├── searches/          # Search management pages
│   │   ├── listings/          # Listings browser
│   │   ├── settings/          # Settings page
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   │   ├── ui/               # Reusable UI components
│   │   ├── Navigation.tsx    # Sidebar navigation
│   │   └── DashboardLayout.tsx # Protected layout wrapper
│   └── lib/
│       ├── api/              # API client and endpoints
│       ├── hooks/            # Custom React hooks
│       ├── stores/           # Zustand stores
│       ├── types/            # TypeScript types
│       └── utils/            # Utility functions
├── public/                   # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## Key Components

### API Client

The API client (`src/lib/api/client.ts`) handles:
- Automatic JWT token management
- Token refresh on 401 errors
- Request/response interceptors
- LocalStorage persistence

### Custom Hooks

- `useAuth` - Authentication state and methods
- `useSearches` - Search CRUD operations
- `useListings` - Listing management and filtering
- `useDashboard` - Dashboard statistics

### Protected Routes

All dashboard routes are protected by the `DashboardLayout` component, which:
- Checks authentication status
- Redirects to login if not authenticated
- Shows loading spinner during auth check

## API Integration

The frontend communicates with the FastAPI backend:

- **Base URL**: `http://localhost:8000/api/v1`
- **Authentication**: JWT tokens in `Authorization` header
- **Endpoints**:
  - `/auth/*` - Authentication
  - `/searches/*` - Search management
  - `/listings/*` - Listing operations
  - `/dashboard/stats` - Dashboard statistics

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_API_VERSION` | API version | `v1` |
| `NEXT_PUBLIC_APP_NAME` | Application name | `Deal Scout` |

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import project in Vercel
3. Set environment variables
4. Deploy

### Docker

```bash
# Build
docker build -t deal-scout-frontend .

# Run
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://api:8000 deal-scout-frontend
```

### Manual

```bash
npm run build
npm start
```

## Future Enhancements

- [ ] Real-time notifications with WebSockets
- [ ] Advanced filtering and sorting
- [ ] Export listings to CSV/PDF
- [ ] Alert configuration UI
- [ ] User profile editing
- [ ] Dark mode toggle
- [ ] PWA support
- [ ] Email/SMS notification preferences

## Contributing

1. Create a feature branch
2. Make your changes
3. Run type checking and linting
4. Submit a pull request

## License

Proprietary - All rights reserved
