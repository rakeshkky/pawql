# PawQL Dashboard UI

A modern, elegant React dashboard for monitoring pet care locations with real-time insights.

## Features

- 🏢 **Location Selection**: Dropdown to select from available pet care locations
- 📊 **Interactive Dashboard**: Rich, visual dashboard with charts and metrics
- 📅 **Date Selection**: View historical data for any date
- 🎨 **Modern UI**: Clean, responsive design with Tailwind CSS
- ⚡ **Fast Loading**: Built with Vite for optimal performance
- 🔒 **Secure**: Environment-based API key management

## Tech Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Chart.js** for data visualization

## Prerequisites

- Node.js 18+ 
- npm or yarn
- PromptQL API key
- DDN token

## Setup

1. **Clone and navigate to the dashboard directory:**
   ```bash
   cd dashboard-ui
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   ```env
   VITE_PROMPTQL_API_KEY=your-promptql-api-key-here
   VITE_DDN_TOKEN=your-ddn-token-here
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

5. **Open your browser:**
   Navigate to `http://localhost:3000`

## Usage

1. **Select Location**: Choose a pet care location from the dropdown
2. **Pick Date**: Select the date you want to view data for
3. **View Dashboard**: The dashboard will automatically load with:
   - Weather information
   - Staff schedules
   - Appointment timeline
   - Revenue metrics
   - Service breakdowns

## API Integration

The app integrates with two PromptQL endpoints:

- `fetch_all_locations` - Retrieves available locations
- `visual_location_dashboard` - Generates dashboard HTML for a specific location and date

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_PROMPTQL_API_KEY` | Your PromptQL API key | Yes |
| `VITE_DDN_TOKEN` | Your DDN authentication token | Yes |

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Error Handling

The app includes comprehensive error handling:
- Missing environment variables will show an error on startup
- API failures display user-friendly error messages with retry options
- Loading states provide visual feedback during data fetching

## Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## License

MIT
