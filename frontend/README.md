# Frontend

React + TypeScript frontend for the Mindhive chatbot.

## Setup

```bash
npm install
npm run dev
```

Frontend: `http://localhost:5173` | Backend: `http://localhost:8000`

## Environment Variables

Create `.env` (optional):

```env
VITE_API_URL=http://localhost:8000
```

## Features

- Chat interface with message list, avatars, timestamps
- Multiline input (Enter to send, Shift+Enter for newline)
- Quick actions: `/calc`, `/products`, `/outlets`, `/reset`
- localStorage persistence
- Error handling with ErrorBoundary

## Components

- **ChatWindow**: Main container
- **MessageList**: Message display with auto-scroll
- **MessageBubble**: Individual message with avatar
- **InputComposer**: Message input with quick actions
- **QuickActions**: Quick action buttons

## Testing

```bash
npm test
npm run test:coverage
```

**34 tests** covering all components and hooks.

## Building

```bash
npm run build
npm run preview
```

## Deployment

### Vercel

1. Connect GitHub repository
2. Set `VITE_API_URL` environment variable
3. Deploy

### Docker

```bash
docker build -t mindhive-frontend .
docker run -p 5173:5173 -e VITE_API_URL=http://your-backend-url mindhive-frontend
```
