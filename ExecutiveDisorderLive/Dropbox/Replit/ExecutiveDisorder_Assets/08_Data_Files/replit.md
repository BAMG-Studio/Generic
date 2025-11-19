# Executive Disorder - Political Satire Game

## Overview

Executive Disorder is a humorous political decision-making game built as a web application. Players select a satirical political character and make decisions through a series of cards that affect four key resources: popularity, stability, media perception, and economy. The game features both 2D and 3D rendering capabilities, with a focus on comedic scenarios and absurd political situations. Built with React, TypeScript, and Express, it combines modern web technologies with game mechanics to create an engaging political satire experience.

## Recent Changes

### October 10, 2025 - Complete Asset Consolidation & Video Generation
**Major Update: ExecutiveDisorder_Assets Structure + Runway ML Videos**

Created comprehensive asset organization system with all generated content consolidated:

**ExecutiveDisorder_Assets Structure (190 files, 316.5 MB):**
- **01_Characters/** (60 files, 77 MB) - All 10 character portraits with 6 emotions each
- **02_Decision_Cards/** (future use)
- **03_Endings/** (future use)
- **04_UI_Elements/** (3 files, 3.7 MB) - Logo, backgrounds, UI assets
- **05_Backgrounds/** (105 files, 159 MB) - 15 main scenes + 90 variations
- **06_Audio/** (3 files, 852 KB) - Placeholders awaiting Zapsplat/Mubert
- **07_Effects/** (future use)
- **08_Data_Files/** (5 files, 112 KB) - Complete documentation
- **09_Video_Assets/** (14 files, 79 MB) - Runway ML generated videos
- **10_AI_Generated/** - Tracking logs and attribution
- **11_Localization/** (future use)
- **12_Marketing/** (future use)

**Runway ML Video Generation:**
- 5 animated backgrounds (10s each): Oval Office, Press Room, White House, Breaking News, Rally Stage
- 9 event videos (5s each): Breaking news, economic crash, protest, scandal, victory, defeat, crisis, diplomatic tension, media chaos
- Provider: Runway ML Gen-3 Alpha Turbo
- Total cost: ~$3-5 for all 14 videos
- Format: MP4, 1280x768

**Asset Inventory:**
- Character portraits: 60 files (all 10 characters with emotions)
- Scene images: 105 files (15 main + 90 variations)
- Videos: 14 files (5 backgrounds + 9 events)
- UI elements: 3 files (logo, backgrounds)
- Documentation: Complete manifest and tracking

**Dropbox Sync:**
- All 187 files uploaded to `/Replit/ExecutiveDisorder_Assets/`
- Total uploaded: 313.68 MB
- Status: ✅ Fully synced

**Documentation:**
- `ASSET_MANIFEST.md` - Complete asset inventory with details
- `ASSET_INVENTORY.json` - Machine-readable catalog
- `RUNWAY_STATUS_OCT10.md` - Video generation status
- `VARIATIONS_COMPLETE_OCT10.md` - Scene variation guide

## User Preferences

**Communication Style:** Simple, everyday language.

**Asset Management Workflow:**
- **Primary Storage:** All generated assets automatically saved to `Dropbox/Replit/ExecutiveDisorder_Assets/`
- **Organized by 12 categories:**
  - `01_Characters/` - Character portraits and emotions
  - `02_Decision_Cards/` - Card visuals (future)
  - `03_Endings/` - Ending screens (future)
  - `04_UI_Elements/` - Logo, backgrounds, buttons
  - `05_Backgrounds/` - Scene images and variations
  - `06_Audio/` - Sound effects and music
  - `07_Effects/` - Visual effects (future)
  - `08_Data_Files/` - Documentation and tracking
  - `09_Video_Assets/` - Animated backgrounds and events
  - `10_AI_Generated/` - Generation logs and attribution
  - `11_Localization/` - Multi-language assets (future)
  - `12_Marketing/` - Promotional materials (future)
- **Naming Convention:** Lowercase-hyphen-separated (e.g., `character-name-emotion.png`)
- **Documentation:** Complete manifest in `ASSET_MANIFEST.md`
- **Dropbox Backend:** All assets synced to `/Replit/ExecutiveDisorder_Assets/`

## System Architecture

### Frontend Architecture

**Framework & Build System**
- React 18 with TypeScript for type-safe component development
- Vite as the build tool and development server, configured with React plugin and GLSL shader support
- Client code organized in `/client/src` with path aliases (`@/` for client source, `@shared/` for shared code)

**UI Component System**
- Radix UI primitives for accessible, unstyled components (dialogs, dropdowns, accordions, etc.)
- Tailwind CSS for utility-first styling with custom theme configuration
- Custom design system with HSL-based color tokens for theming
- shadcn/ui patterns for consistent component architecture

**Game Rendering**
- Dual rendering approach: 2D DOM-based and 3D WebGL (Three.js via React Three Fiber)
- React Three Fiber with Drei and Postprocessing for 3D scenes
- 2D implementation as primary interface, with 3D components available for enhanced visuals
- Support for GLTF/GLB 3D models and GLSL shaders via vite-plugin-glsl

**State Management**
- Zustand stores for game state management:
  - `useGameState`: Game phase, turn counter, time of day
  - `useCharacters`: Character selection and data
  - `useResources`: Resource tracking (popularity, stability, media, economy)
- React Query (@tanstack/react-query) for server state management
- Local storage integration for persistence

**Game Flow**
- Three main phases: character selection → playing → game ending
- Card-based decision system with multiple choice options
- Resource management affecting game outcomes
- Turn-based progression with configurable max turns (50)
- Multiple ending scenarios based on total resource scores

### Backend Architecture

**Server Framework**
- Express.js server with TypeScript
- ESM module system throughout the stack
- Development server runs via tsx, production builds with esbuild
- Vite middleware integration for HMR in development

**API Design**
- RESTful API pattern (routes prefixed with `/api`)
- Centralized route registration in `/server/routes.ts`
- Error handling middleware with status code normalization
- Request/response logging with duration tracking

**Storage Layer**
- Abstract storage interface pattern (`IStorage`) for data operations
- In-memory storage implementation (`MemStorage`) as default
- CRUD methods for user management (getUser, getUserByUsername, createUser)
- Database-agnostic design allowing swap to persistent storage

### Data Storage Solutions

**Database Configuration**
- Drizzle ORM configured for PostgreSQL via `@neondatabase/serverless`
- Schema definition in `/shared/schema.ts` for code sharing between client/server
- Migration system configured to output to `/migrations` directory
- Zod integration for runtime validation via drizzle-zod

**Data Models**
- User table with id, username (unique), and password fields
- Type-safe schema inference using Drizzle's type system
- Insert schemas generated from table definitions with validation

**Session Management**
- Connect-pg-simple configured for PostgreSQL session storage
- Cookie-based session handling with Express

### External Dependencies

**Database & ORM**
- Neon serverless PostgreSQL (`@neondatabase/serverless`)
- Drizzle ORM with PostgreSQL dialect for type-safe database queries
- Database connection via `DATABASE_URL` environment variable

**3D Graphics & Rendering**
- Three.js for WebGL rendering
- React Three Fiber (@react-three/fiber) for declarative 3D scenes
- Drei (@react-three/drei) for Three.js helpers and abstractions
- Postprocessing (@react-three/postprocessing) for visual effects

**UI & Styling**
- Radix UI component primitives (20+ component packages)
- Tailwind CSS with PostCSS and Autoprefixer
- Inter font (@fontsource/inter) for typography
- Class Variance Authority (CVA) for component variant styling

**Utilities & Tooling**
- date-fns for date manipulation
- cmdk for command menu functionality
- nanoid for unique ID generation
- Zod for runtime type validation

**Development Tools**
- Replit-specific Vite plugin for error overlays
- TypeScript with strict mode enabled
- Path aliases for clean imports
- GLSL shader support via vite-plugin-glsl

**Asset Support**
- Image formats: standard web formats
- 3D models: GLTF, GLB
- Audio: MP3, OGG, WAV files
- Font formats: JSON-based font files