# Mindhive AI Chatbot - Frontend

React + TypeScript frontend for the Mindhive multi-agent chatbot. Built with Vite, TailwindCSS, and shadcn/ui components.

## Tech Stack

- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS with dark mode support
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Icons**: Lucide React
- **Testing**: Vitest + Testing Library
- **State Management**: React Hooks + localStorage

## Project Structure

```
frontend/
├── src/
│   ├── components/        # React components
│   │   ├── ChatWindow.tsx      # Main chat container with ErrorBoundary
│   │   ├── MessageList.tsx     # Message display with auto-scroll
│   │   ├── MessageBubble.tsx   # Individual message with avatar, timestamp
│   │   ├── InputComposer.tsx   # Multiline input (Enter to send, Shift+Enter for newline)
│   │   ├── QuickActions.tsx    # Quick action buttons (/calc, /products, /outlets, /reset)
│   │   ├── ToolCallCard.tsx    # Expandable tool call visualization
│   │   ├── BackendStatus.tsx   # Health check indicator (30s polling)
│   │   ├── ErrorBoundary.tsx   # Error boundary wrapper
│   │   └── ui/                 # shadcn/ui components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── input.tsx
│   │       ├── textarea.tsx
│   │       └── alert.tsx
│   ├── hooks/             # Custom React hooks
│   │   └── useChat.ts          # Chat state management
│   ├── services/          # API service layer
│   │   └── api.ts              # Backend API calls with TypeScript types
│   ├── utils/             # Utilities
│   │   └── localStorage.ts     # Conversation persistence
│   ├── lib/               # Library utilities
│   │   └── utils.ts            # Utility functions (cn for className merging)
│   ├── test/              # Test setup
│   │   └── setup.ts            # Vitest setup with testing-library
│   ├── App.tsx            # Root component
│   └── main.tsx           # Entry point
├── package.json
├── vite.config.ts         # Vite configuration
├── vitest.config.ts       # Vitest configuration
├── tailwind.config.js     # TailwindCSS configuration
├── tsconfig.json          # TypeScript configuration
└── Dockerfile             # Frontend containerization
```

## Setup

### Prerequisites

- Node.js 18+ and npm
- Backend server running (see [Backend README](../backend/README.md))

### Installation

1. **Navigate to frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Set up environment variables (optional):**

   ```bash
   # Create .env file
   echo "VITE_API_URL=http://localhost:8000" > .env
   ```

   Defaults to `http://localhost:8000` if not set.

## Running the Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` and will connect to the backend at `http://localhost:8000` (or your configured `VITE_API_URL`).

## Building for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

Preview the production build:

```bash
npm run preview
```

## Testing

Run tests:

```bash
npm test
```

Run tests with UI:

```bash
npm run test:ui
```

Run tests with coverage:

```bash
npm run test:coverage
```

## Features

### Chat Interface

- **Message List**: Displays messages with avatars, timestamps, and multi-turn threading
- **Auto-scroll**: Automatically scrolls to bottom on new messages
- **Message Types**: User messages (right-aligned) and bot messages (left-aligned)

### Input Composer

- **Multiline Input**: Textarea supports multiple lines
- **Enter to Send**: Press Enter to send message
- **Shift+Enter**: Press Shift+Enter for newline
- **Quick Actions**: Dropdown with `/calc`, `/products`, `/outlets`, `/reset` commands
- **Auto-complete**: Quick actions autocomplete as you type

### Tool Call Visualization

- **ToolCallCard**: Expandable cards showing tool calls
- **Tool Types**: Calculator, Products, Outlets
- **Status Indicators**: Success (green), Error (red)
- **Expandable JSON**: View tool inputs and outputs in formatted JSON

### Backend Status

- **Health Check**: Polls `/health` endpoint every 30 seconds
- **Visual Indicator**: Green checkmark (online) or red X (offline)
- **Responsive**: Hides text on small screens, shows icon only

### Persistence

- **localStorage**: Saves conversation history to browser storage
- **Auto-restore**: Loads conversation on page refresh
- **Clear on Reset**: Clears history when `/reset` command is used

### Error Handling

- **ErrorBoundary**: Catches React errors and displays fallback UI
- **API Errors**: Displays user-friendly error messages
- **Network Errors**: Shows connection status and retry options

## Component Details

### ChatWindow

Main container component that:

- Wraps chat interface with ErrorBoundary
- Manages chat state via `useChat` hook
- Handles message sending and receiving
- Displays BackendStatus indicator

### MessageList

Displays list of messages:

- Auto-scrolls to bottom on new messages
- Shows user and bot messages with different styling
- Displays timestamps
- Renders ToolCallCard for tool calls

### MessageBubble

Individual message component:

- User messages: Right-aligned, blue background
- Bot messages: Left-aligned, gray background
- Shows avatar (user icon or bot icon)
- Displays timestamp
- Handles markdown formatting (if needed)

### InputComposer

Message input component:

- Multiline textarea
- Enter to send, Shift+Enter for newline
- Quick actions dropdown
- Disabled state while sending
- Loading indicator

### QuickActions

Quick action buttons:

- `/calc` - Calculator tool
- `/products` - Product search
- `/outlets` - Outlet search
- `/reset` - Clear conversation
- Auto-completes as you type

### ToolCallCard

Tool call visualization:

- Expandable card showing tool name, status
- Displays tool input and output
- Color-coded borders (green for success, red for error)
- Formatted JSON view

### BackendStatus

Health check indicator:

- Polls `/health` endpoint every 30 seconds
- Shows connection status
- Responsive design (icon only on mobile)

## API Integration

The frontend communicates with the backend via the `api.ts` service:

```typescript
// Example API calls
import {
  sendMessage,
  calculate,
  searchProducts,
  searchOutlets,
  checkHealth,
} from "./services/api";

// Send chat message
const response = await sendMessage("Show me tumblers");

// Calculate
const result = await calculate("2 + 2");

// Search products
const products = await searchProducts("tumbler");

// Search outlets
const outlets = await searchOutlets("outlets in petaling jaya");

// Check health
const health = await checkHealth();
```

All API functions return typed Promise responses and handle errors gracefully.

## Environment Variables

| Variable       | Description     | Default                 |
| -------------- | --------------- | ----------------------- |
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

## Styling

The frontend uses TailwindCSS with:

- Dark mode support (system preference)
- Custom color scheme
- Responsive design (mobile-first)
- Animations via `tailwindcss-animate`

## Testing

Tests are written using:

- **Vitest**: Test runner
- **@testing-library/react**: React component testing
- **@testing-library/user-event**: User interaction testing
- **@testing-library/jest-dom**: DOM matchers

Example test:

```typescript
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import MessageBubble from "./MessageBubble";

describe("MessageBubble", () => {
  it("renders user message", () => {
    render(<MessageBubble role="user" content="Hello" />);
    expect(screen.getByText("Hello")).toBeInTheDocument();
  });
});
```

## Deployment

### Vercel

1. Connect your GitHub repository to Vercel
2. Set `VITE_API_URL` environment variable
3. Deploy - Vercel will auto-detect Vite

### Docker

```bash
# Build image
docker build -t mindhive-frontend .

# Run container
docker run -p 5173:5173 -e VITE_API_URL=http://your-backend-url mindhive-frontend
```

Or use `docker-compose.yml` from root directory.

## Troubleshooting

### API Connection Issues

- Check `VITE_API_URL` matches backend URL
- Ensure backend server is running
- Check browser console for CORS errors

### Build Errors

- Run `npm install` to ensure all dependencies are installed
- Check TypeScript errors: `npm run build`
- Clear node_modules and reinstall if needed

### Styling Issues

- Ensure TailwindCSS is properly configured
- Check `tailwind.config.js` for correct content paths
- Verify PostCSS configuration

## License

Part of the Mindhive technical assessment project.
