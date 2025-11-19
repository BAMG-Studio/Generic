# Executive Disorder - Political Satire Game

## Overview

Executive Disorder is a humorous political decision-making game built as a web application. Players select a satirical political character and make decisions through a series of cards that affect four key resources: popularity, stability, media perception, and economy. The game features both 2D and 3D rendering capabilities, with a focus on comedic scenarios and absurd political situations. Built with React, TypeScript, and Express, it combines modern web technologies with game mechanics to create an engaging political satire experience.

## Recent Changes

### October 10, 2025 - Scene Background Variations
**Asset Expansion: 90 Scene Variations Generated**

Generated 6 atmospheric variations for each of the 15 main scene backgrounds, creating 90 new scene assets:

- **Backgrounds** (24 variations): Oval Office, White House Exterior, Press Room, Situation Room
- **Crisis Scenes** (18 variations): Economic Crisis, Natural Disaster, Cyber Attack  
- **Meeting Rooms** (18 variations): Cabinet Room, International Summit, UN Assembly
- **News Scenes** (12 variations): TV Studio, Breaking News Set
- **Public Spaces** (18 variations): Rally Stage, Protest Square, Airport Arrival

**Variation Types:**
- Time of day: night, dawn, dusk, sunset, sunrise
- Weather conditions: storm, rain, snow, clear
- Camera perspectives: aerial, reverse angle, first-person POV
- Mood variations: crisis, celebration, empty/preparation, chaos

**Storage & Organization:**
- All 90 variations saved to `Dropbox/Replit/Scenes/*/Variations/` folders
- Proper naming: lowercase-hyphen-separated (e.g., `oval-office-night.png`)
- Total size: ~137MB
- Uploaded to Dropbox backend via upload script

**Asset Inventory:**
- Previous: 15 main scene backgrounds
- New: 90 variations (6 per scene)
- **Total: 105 scene assets** (+600% increase)

**Documentation:**
- `VARIATIONS_COMPLETE_OCT10.md` - Comprehensive guide with all variations
- `FILE_MANIFEST_VARIATIONS.md` - Complete file listing with sizes
- `UPLOAD_VERIFICATION_LOG.md` - Upload execution details

## User Preferences

**Communication Style:** Simple, everyday language.

**Asset Management Workflow:**
- All generated assets (images, 3D models, etc.) must be automatically saved to `Dropbox/Replit/` folder
- Assets should be intelligently categorized by type:
  - Character images → `Dropbox/Replit/characters/`
  - Logos/branding → `Dropbox/Replit/logos/`
  - 3D models → `Dropbox/Replit/models/`
  - UI elements → `Dropbox/Replit/ui-assets/`
  - Generated images → `Dropbox/Replit/generated-images/`
- Use proper naming conventions: lowercase, hyphen-separated (e.g., `character-name-emotion.png`)
- Create subdirectories as needed for variations (e.g., `main-portraits/`, `variations/`)
- Always include a README.md in the Dropbox/Replit folder documenting the archive structure

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