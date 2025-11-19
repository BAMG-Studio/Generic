# Executive Disorder - Political Satire Game

## Overview

Executive Disorder is a humorous political decision-making web application where players choose a satirical political character and navigate decisions affecting popularity, stability, media perception, and economy. The game features a dual 2D/3D rendering approach, focusing on comedic, absurd political scenarios. Built with React, TypeScript, and Express, it aims to create an engaging satirical experience combining modern web technologies with game mechanics. The game has significantly expanded its scope with AI-powered content generation, offering a richer and more dynamic gameplay experience, including 12 characters, over 150 decision cards, 50 crisis events, and 20 unique endings.

## User Preferences

**Communication Style:** Simple, everyday language.

**Asset Management Workflow:**
- **Primary Storage:** All generated assets automatically saved to `Dropbox/Replit/ExecutiveDisorder_Assets/`
- **Organized by 12 categories:**
  - `01_Characters/` - Character portraits, emotions, expressions, and character cards
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

### Content Generation Workflow

The game utilizes a two-phase architecture:
-   **Phase 1: Pre-generation:** All game assets (cards, leaders, crises, endings, images, audio) are generated once using AI APIs (ElevenLabs, Runway ML) and exported to static JSON/YAML files and the Dropbox/Replit folder. AI APIs are **only** used in this phase.
-   **Phase 2: Game Runtime:** The game loads pre-generated assets from static files. There are **no API calls during gameplay**; all assets are static.

### Frontend Architecture

-   **Framework & Build System:** React 18 with TypeScript, Vite, and GLSL shader support.
-   **Routing System:** A page-based architecture using `wouter` for navigation between 5 distinct pages: Title, Menu, Character Select, Character Stats, and Game.
-   **UI/UX Decisions:**
    -   **Glassmorphic UI:** All elements use semi-transparent backgrounds (20-60% opacity) with `backdrop-blur`.
    -   **Styling:** Tailwind CSS, custom HSL-based color tokens, and `shadcn/ui` patterns.
    -   **Typography:** Google Fonts - Space Grotesk (headings), Inter (UI text) with preconnect optimization.
    -   **Animations:** 10 custom Framer Motion animations (fadeIn, slideUp/Down, float, glow, gradient, shimmer).
    -   **Color Schemes:** Title uses a bold rainbow gradient. Menu features dark gradients, animated grid overlays, and a scrolling ticker. Characters are displayed in a card-based grid with hover glow effects.
    -   **Templates:** Modern card grid for the menu, grid for character selection, and a split-view design for the game page.
    -   **Responsive Design:** Mobile-first approach optimized for all devices (Samsung Galaxy S24 Ultra, iPhones, tablets, laptops).
    -   **Accessibility:** WCAG-compliant focus rings, reduced motion support, high contrast mode, screen reader utilities.
-   **Game Rendering:** Multi-page approach. Future plans include dual 2D DOM-based and 3D WebGL (Three.js via React Three Fiber) rendering.
-   **State Management:** Zustand for core game state, React Query for server state, and local storage for persistence.
-   **Game Flow:** Title → Menu → Character Selection → Character Stats → Game. Turn-based progression with multiple endings.
-   **Asset Loading:** Each page loads only necessary assets from static files.

### Backend Architecture

-   **Server Framework:** Express.js with TypeScript, ESM modules, and `tsx` for development.
-   **API Design:** RESTful API with centralized route registration, error handling, and request/response logging.
-   **Storage Layer:** Abstract storage interface with an in-memory implementation (`MemStorage`) designed for database-agnostic operations.

### Data Storage Solutions

-   **Database Configuration:** Drizzle ORM for PostgreSQL via `@neondatabase/serverless`, with schema defined in `/shared/schema.ts`.
-   **Data Models:** User table with id, unique username, and password, validated with Zod.
-   **Session Management:** `connect-pg-simple` for PostgreSQL session storage with cookie-based handling.

## External Dependencies

-   **Database & ORM:** Neon serverless PostgreSQL, Drizzle ORM.
-   **3D Graphics & Rendering:** Three.js, React Three Fiber, Drei, Postprocessing.
-   **UI & Styling:** Radix UI, Tailwind CSS, Space Grotesk + Inter fonts, Class Variance Authority (CVA), Framer Motion.
-   **Utilities & Tooling:** date-fns, cmdk, nanoid, Zod, wouter.
-   **Development Tools:** Replit-specific Vite plugin, TypeScript, Path aliases, `vite-plugin-glsl`.
-   **Responsive Features:** Mobile-optimized viewport, PWA-ready meta tags, safe area support, touch-friendly tap targets.
-   **Asset Support:** Standard web image formats, GLTF/GLB 3D models, MP3/OGG/WAV audio, JSON-based fonts.
-   **AI Content Generation (Pre-generation phase only):** ElevenLabs, Runway ML Gen3a Turbo, Google Veo3.