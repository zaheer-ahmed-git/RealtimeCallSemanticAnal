# 04 - Frontend and User Flow Deep Dive

## 1. Frontend stack
- Framework: Next.js 14 (App Router)
- Language: TypeScript
- UI: React + Tailwind CSS
- Charts: Recharts
- HTTP: Axios
- Notifications: react-hot-toast

## 2. Frontend structure

Main directories:
- `frontend/src/app/`
  - `page.tsx` (main one-page app)
  - `layout.tsx` (global layout + navbar + toasts)
  - `results/[callId]/page.tsx` (result detail route)
  - `history/page.tsx` and `about/page.tsx` redirect to anchored sections
- `frontend/src/components/`
  - Upload, dashboard, chart, history, about, and navigation components
- `frontend/src/lib/`
  - `api.ts` (typed API layer)
  - `types.ts` (interfaces)

## 3. API communication design

### Proxy strategy
`next.config.js` rewrites:
- `/api/:path*` -> `http://localhost:8000/api/:path*`

This avoids direct cross-origin complexity during local development.

### API client behavior (`src/lib/api.ts`)
- Centralized Axios client with timeout
- Normalizes numbers/status and backend payload shape
- Converts backend variation into stable frontend types
- Exposes functions:
  - uploadAudio
  - analyzeCall
  - getStatus
  - getResults
  - getHistory
  - exportJSON/PDF/CSV

## 4. Main page runtime flow (`src/app/page.tsx`)
State variables managed on page:
- uploaded file metadata
- analysis status/progress
- analysis results payload
- loading flags

User flow:
1. Upload file via `UploadForm`.
2. Click `Run Analysis`.
3. Frontend posts `call_id` to `/api/analyze`.
4. Polls `/api/status/{call_id}` every 2s.
5. On `completed`, fetches `/api/results/{call_id}`.
6. Renders `AnalysisDashboard`.

## 5. Key components and what each does

### `UploadForm.tsx`
- Validates type/size before upload
- Accepts `.wav/.mp3/.m4a`
- Sends file as multipart using `apiService.uploadAudio`

### `AnalysisDashboard.tsx`
- Summary cards (sentiment, sale probability, duration, participants)
- Tabbed sections:
  - Overview
  - Sentiment
  - Emotions
  - Key phrases
- Export actions for PDF/CSV/JSON

### Chart components
- `SentimentChart.tsx`: line chart by timestamp index
- `EmotionChart.tsx`: pie chart for emotion distribution
- `SaleGauge.tsx`: radial gauge style probability display
- `KeyPhrases.tsx`: positive vs negative phrase lists

### `HistorySection.tsx`
- Fetches `/api/history`
- Displays status, metadata, and quick link to result page

## 6. Type contracts
`src/lib/types.ts` defines stable contracts for:
- upload/analyze/status responses
- sentiment point type
- key phrase type
- call results shape
- history item shape

This is important in viva because it shows strong typed integration rather than ad hoc JSON handling.

## 7. UX behavior worth highlighting
- Asynchronous progress polling with graceful timeout fallback
- Toast-based user feedback for success/failure
- Dedicated result route (`/results/[callId]`) and history navigation
- Built-in export actions from analyzed results

## 8. Frontend strengths to present
- Clean separation of API logic from UI components
- Good typed boundary between backend and frontend
- Practical end-user flow from upload to insight and export
- Componentized chart dashboard for modular extension

## 9. Frontend limitations and improvement path
1. Visual style is currently dark and expressive but can improve contrast consistency in some cards.
2. Progress UI is polling-based; WebSockets would reduce repeated requests.
3. Upload component has a progress bar state, but no streaming progress feed from backend transfer chunks.
4. Anchored single-page sections are practical, but deeper route-level segmentation could improve scalability.

## 10. Why the frontend design is defendable in evaluation
- It is not just static UI; it is fully wired to backend lifecycle events.
- It handles real async workflows and partial failure conditions.
- It presents business-facing outputs in a clear, actionable structure.
