# Page-Based Architecture Implementation

## Overview
Executive Disorder has been transformed from a single-page app to a multi-page routing architecture. This allows each scene to load only the assets it needs (decision cards, backgrounds, UI elements, effects, audio, video) without overwhelming a single page.

## Architecture Benefits
✅ **Clean Separation** - Each page loads independently with its own assets
✅ **Better Performance** - Only load what's needed for each scene
✅ **Easier Maintenance** - Pages are isolated and easier to debug
✅ **Rich Media Support** - Each page can load videos, audio, effects without conflicts
✅ **Scalable** - Easy to add new pages/scenes without affecting others

## Page Structure

### 1. Title Page (`/`)
**File:** `client/src/pages/TitlePage.tsx`

**Features:**
- Bold rainbow gradient title: EXECUTIVE DISORDER
- Animated particle background (deterministic, SSR-safe)
- Click-to-enter button with hover effects
- Game tagline and description

**Navigation:** Click "ENTER" → Menu Page

### 2. Menu Page (`/menu`)
**File:** `client/src/pages/MenuPage.tsx`

**Features:**
- Modern card-based layout (2×2 grid)
- Animated headline ticker at top
- 4 menu options: New Game, Continue, Character Gallery, Settings
- Stats footer with game metrics

**Navigation:** 
- "New Game" → Character Select Page
- "Character Gallery" → Character Select Page

### 3. Character Select Page (`/character-select`)
**File:** `client/src/pages/CharacterSelectPage.tsx`

**Features:**
- Grid layout: 2 cols mobile, 3 cols tablet, 6 cols desktop
- 12 character cards with portraits
- Hover effects: scale, glow, border highlight
- Stats preview on each card
- Back to Menu button

**Navigation:** Click character → Character Stats Page (`/character/:id`)

### 4. Character Stats Page (`/character/:id`)
**File:** `client/src/pages/CharacterStatsPage.tsx`

**Features:**
- Large character portrait (3:4 aspect ratio)
- Full biography display
- Animated stats bars (Popularity, Stability, Media, Economy)
- Special abilities list with bullets
- "START CAMPAIGN" button

**State Updates:**
- Calls `setSelectedCharacter(character)` 
- Sets `resources` to character's starting stats
- Calls `startGame()` to set game phase

**Navigation:** Click "START CAMPAIGN" → Game Page (`/game`)

### 5. Game Page (`/game`)
**File:** `client/src/pages/GamePage.tsx`

**Features:**
- **Side-by-side layout:**
  - **Left:** Dynamic background scene/event visualization
  - **Right:** Decision card with options
- Top HUD with character info and resource bars
- Audio/effect indicators
- Exit to menu button

**Guard:** Redirects to `/character-select` if no character selected (via useEffect)

**Decision Flow:**
1. Display current decision card
2. Show options (A, B, C)
3. Player clicks option
4. Call `makeDecision(cardId, optionIndex)`
5. Advance turn
6. Load next card

## Routing Implementation

### Using wouter
```tsx
import { Route } from "wouter";

function App() {
  return (
    <AppShell>
      <Route path="/" component={TitlePage} />
      <Route path="/menu" component={MenuPage} />
      <Route path="/character-select" component={CharacterSelectPage} />
      <Route path="/character/:id" component={CharacterStatsPage} />
      <Route path="/game" component={GamePage} />
    </AppShell>
  );
}
```

**Note:** No `<Router>` wrapper needed with wouter

### Navigation Between Pages
```tsx
import { useLocation } from "wouter";

function MyComponent() {
  const [, setLocation] = useLocation();
  
  const goToMenu = () => {
    setLocation("/menu");
  };
}
```

## State Management

### Extended GameState
```typescript
interface GameState {
  // Existing
  gamePhase: GamePhase;
  timeOfDay: TimeOfDay;
  turn: number;
  isLoading: boolean;
  
  // New additions
  selectedCharacter: PoliticalCharacter | null;
  resources: {
    popularity: number;
    stability: number;
    media: number;
    economy: number;
  };
  
  // New actions
  setSelectedCharacter: (character: PoliticalCharacter) => void;
  startGame: () => void;
  makeDecision: (cardId: string, optionIndex: number) => void;
}
```

### State Flow
1. **Character Selection:** `setSelectedCharacter(character)` sets character + starting resources
2. **Game Start:** `startGame()` changes phase to "playing"
3. **Decision Making:** `makeDecision(cardId, optionIndex)` applies effects and advances turn

## Design System

### Glassmorphic UI Philosophy
**Executive Disorder uses translucent glassmorphic design to allow simultaneous display of multiple media assets:**
- All UI elements use semi-transparent backgrounds (20-60% opacity)
- Backdrop-blur effects create depth and definition
- Background videos/images show through all overlays
- Text maintains readability with proper contrast
- Borders use 20-40% white opacity for subtle definition

### Color Palette
- **Title:** Rainbow gradient (amber → red → pink → purple → blue)
- **Menu:** Indigo/purple gradient with translucent card-based layout
- **Character Select:** Slate/indigo/purple gradient with glass cards
- **Character Stats:** Purple/indigo with yellow accents and glass panels
- **Game:** Dark slate with translucent decision cards over dynamic backgrounds

### Glassmorphic Components
- **Headers/HUD:** `bg-black/20 backdrop-blur-md border-white/20`
- **Decision Cards:** `bg-slate-900/40 to-slate-950/60 backdrop-blur-xl border-white/30`
- **Info Panels:** `bg-black/20 backdrop-blur-lg border-white/20`
- **Menu Cards:** `bg-gradient/40-60 backdrop-blur-lg border-white/20`
- **Character Cards:** `bg-slate-900/40 to-slate-950/60 backdrop-blur-lg`
- **Overlays:** `bg-black/20-80 backdrop-blur-sm` (varies by depth)

### Typography
- **Titles:** Bold, large scale (7xl - 9xl)
- **Headings:** 2xl - 4xl, white with gradients
- **Body:** lg - xl, white/90 opacity (increased from 80 for readability)
- **Accents:** Yellow-400 for highlights
- **Contrast:** All text uses white/90 or higher over translucent backgrounds

### Animations
- Framer Motion for page transitions
- Particle animations (deterministic)
- Hover effects on cards (scale, glow, border highlight)
- Stats bar fill animations with gradient
- Button hover/tap feedback with scale transforms
- Glassmorphic shine effects on interaction

## Technical Decisions

### Why Page-Based?
1. **Asset Loading:** Each page loads only what it needs (videos, audio, effects)
2. **Performance:** No single bloated component with all game logic
3. **Maintainability:** Pages are isolated and easier to debug
4. **User Experience:** Clean transitions between game stages
5. **Rich Media:** Can load different background videos per page without conflicts

### Render Safety
- **No Math.random() in render:** Use `useMemo` to pre-compute
- **No window.* in render:** Calculate once, not on every render
- **No navigation in render:** Use `useEffect` for redirects
- **Deterministic animations:** Use index-based calculations

### Data Structure Alignment
- Character IDs are `string` (not number)
- Use `portraitUrl` (not `portrait`)
- Use `fullBio` (not `bio`)
- Use `abilities` array (not single `trait`)
- Decision cards use `options` (not `choices`)

## Navigation Map
```
/
├─ CLICK TO ENTER
│
/menu
├─ NEW GAME → /character-select
├─ CONTINUE → (no save found alert)
├─ CHARACTER GALLERY → /character-select
└─ SETTINGS → (coming soon alert)
   
/character-select
├─ Character Card Click → /character/:id
└─ BACK TO MENU → /menu
   
/character/:id
├─ START CAMPAIGN → /game
└─ BACK → /character-select
   
/game
├─ Make Decision → Next card
├─ EXIT TO MENU → /menu
└─ No Character? → /character-select (auto-redirect)
```

## Adding New Pages

### Step 1: Create Page Component
```tsx
// client/src/pages/MyNewPage.tsx
import { motion } from "framer-motion";
import { useLocation } from "wouter";

export default function MyNewPage() {
  const [, setLocation] = useLocation();
  
  return (
    <div className="relative w-full h-full overflow-hidden">
      {/* Page content */}
    </div>
  );
}
```

### Step 2: Add Route
```tsx
// client/src/App.tsx
import MyNewPage from "./pages/MyNewPage";

<Route path="/my-new-page" component={MyNewPage} />
```

### Step 3: Navigate to Page
```tsx
setLocation("/my-new-page");
```

## Asset Loading Strategy

### Per-Page Assets
- **Title Page:** Particle animations only
- **Menu Page:** Background gradient, ticker data
- **Character Select:** Character portraits (all 12)
- **Character Stats:** Single character portrait + data
- **Game Page:** Decision cards, background scenes, effects

### Background Videos Implemented
**All pages now feature dynamic video backgrounds:**

**MenuPage:**
- Video: capitol-building-exterior.mp4 (static)
- Shows majestic government building

**CharacterSelectPage:**
- Video: government-office-ambient.mp4 (static)
- Professional office atmosphere

**CharacterStatsPage:**
- Dynamic videos based on character (12 mappings)
- Examples: Tech → stock markets, Progressive → protests, Media → breaking news
- Thematically appropriate for each leader

**GamePage:**
- Main background: political-rally-crowd.mp4
- Event panel: Dynamic based on card category
- Categories: crisis, scandal, economic, policy, military, rally, protest
- Videos change with each decision card

**Technical Details:**
- All videos: autoPlay, loop, muted, playsInline
- React key prop forces remount on video change
- Gradient overlays provide depth (40-60% opacity)
- Videos visible through glassmorphic UI
- Smooth transitions between scenes

### Future Enhancements
- Add ending cinematic videos for game conclusions
- Implement audio tracks with video backgrounds
- Preload next video for seamless transitions
- Add video effects for crisis events

## Testing Checklist

### Navigation Flow
- [ ] Title → Menu works
- [ ] Menu → Character Select works
- [ ] Character Select → Character Stats works
- [ ] Character Stats → Game works
- [ ] Game → Menu works
- [ ] Direct URL access to /game redirects if no character
- [ ] Browser refresh maintains state (via Zustand)

### Visual Verification
- [ ] Title screen has animated particles
- [ ] Menu cards have hover effects
- [ ] Character grid shows all 12 characters
- [ ] Character stats display correctly
- [ ] Game page shows side-by-side layout
- [ ] HUD displays resources correctly

### State Management
- [ ] Character selection sets resources
- [ ] Game start changes phase
- [ ] Decision making advances turn
- [ ] Resources update after decisions
- [ ] State persists through navigation

## Known Limitations
- Game state resets on full page refresh (Zustand default behavior)
- No save/load system yet (Continue button disabled)
- Settings page not implemented yet
- Decision effects not fully connected to card data

## Future Improvements
1. Add localStorage persistence for game state
2. Implement save/load system
3. Add settings page with audio controls
4. Connect decision effects to resource changes
5. Add ending cinematics page
6. Implement crisis events page
7. Add achievements/stats page
