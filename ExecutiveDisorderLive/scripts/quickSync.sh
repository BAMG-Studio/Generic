#!/bin/bash
# Quick sync remaining files
echo "🔄 Resuming Dropbox sync..."
tsx scripts/syncToDropbox.ts &
echo "✅ Sync running in background (PID: $!)"
echo "📊 Check progress with: ps aux | grep syncToDropbox"
