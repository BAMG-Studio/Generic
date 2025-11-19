# Replay Loop Videos

**9 seamless looping backgrounds for Executive Disorder gameplay**

## Quick Reference

| Video | Size | Theme | Best For |
|-------|------|-------|----------|
| `government-office-ambient.mp4` | 5.2 MB | Formal office | Decision screens |
| `political-rally-crowd.mp4` | 19 MB | Rally energy | Popularity events |
| `breaking-news-ticker.mp4` | 13 MB | News urgency | Media events |
| `capitol-building-exterior.mp4` | 12 MB | Government power | Legislative moments |
| `press-conference-room.mp4` | 7.2 MB | Official statements | Public announcements |
| `protest-demonstration.mp4` | 18.7 MB | Civil activism | Stability crisis |
| `campaign-headquarters.mp4` | 11.2 MB | Campaign chaos | Election events |
| `stock-market-displays.mp4` | 14.3 MB | Financial data | Economy display |
| `media-circus-exterior.mp4` | 11.4 MB | Media frenzy | Scandal moments |

## Features

✅ **8-second seamless loops** - Designed for continuous playback  
✅ **HD quality (1280x720)** - Crisp visuals optimized for web  
✅ **Political satire themes** - Matches Executive Disorder tone  
✅ **Event-specific** - Different loops for different game moments  
✅ **~112 MB total** - Optimized file sizes  

## How to Use

### Basic Implementation:
```tsx
<video autoPlay muted loop className="absolute inset-0 object-cover">
  <source src="/videos/replay-loops/government-office-ambient.mp4" type="video/mp4" />
</video>
```

### Dynamic Background Based on Game State:
```tsx
const bgVideo = resources.stability < 30 
  ? '/videos/replay-loops/protest-demonstration.mp4'
  : '/videos/replay-loops/government-office-ambient.mp4';

<video src={bgVideo} autoPlay muted loop />
```

## Thematic Groups

**Authority & Power:**
- government-office-ambient
- capitol-building-exterior
- press-conference-room

**Public & Engagement:**
- political-rally-crowd
- protest-demonstration
- campaign-headquarters

**Media:**
- breaking-news-ticker
- media-circus-exterior

**Economy:**
- stock-market-displays

## File Locations

**Dropbox:** `/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Replay_Loop_Videos/`  
**Game Assets:** `client/public/videos/replay-loops/`

## Complete Documentation

See `REPLAY_LOOPS_MANIFEST.md` for:
- Detailed video descriptions
- Integration examples
- Performance optimization tips
- Technical specifications

## Note

9 of 15 planned videos generated (API credit limit reached). The 9 completed videos cover all core political themes for Executive Disorder.
