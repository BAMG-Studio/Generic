#!/bin/bash

# Executive Disorder - Image Upscaling and Optimization Script
# This script upscales all images by 2x and optimizes them for web

echo "🎨 Executive Disorder - Image Upscaling & Optimization"
echo "======================================================"
echo ""

# Create backup directory
BACKUP_DIR="Dropbox/Replit/ExecutiveDisorder_Assets/00_Backups/Original_Images_$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Counter
TOTAL=0
SUCCESS=0
FAILED=0

# Function to upscale and optimize an image
upscale_image() {
    local input="$1"
    local temp="${input}.temp.png"
    
    # Get original dimensions
    DIMS=$(identify -format "%wx%h" "$input" 2>/dev/null)
    if [ -z "$DIMS" ]; then
        echo "  ❌ Failed to read: $input"
        return 1
    fi
    
    WIDTH=$(echo $DIMS | cut -d'x' -f1)
    HEIGHT=$(echo $DIMS | cut -d'x' -f2)
    NEW_WIDTH=$((WIDTH * 2))
    NEW_HEIGHT=$((HEIGHT * 2))
    
    echo "  📐 Upscaling $input from ${WIDTH}x${HEIGHT} to ${NEW_WIDTH}x${NEW_HEIGHT}"
    
    # Backup original
    cp "$input" "$BACKUP_DIR/" 2>/dev/null
    
    # Upscale with Lanczos filter (highest quality) and optimize
    convert "$input" \
        -filter Lanczos \
        -resize ${NEW_WIDTH}x${NEW_HEIGHT} \
        -quality 85 \
        -strip \
        "$temp"
    
    if [ $? -eq 0 ]; then
        mv "$temp" "$input"
        echo "  ✅ Success: $input"
        return 0
    else
        echo "  ❌ Failed: $input"
        rm -f "$temp"
        return 1
    fi
}

# Process character portraits
echo "📸 Processing Character Portraits..."
echo "-----------------------------------"
for img in client/public/characters/*.png; do
    if [ -f "$img" ]; then
        TOTAL=$((TOTAL + 1))
        if upscale_image "$img"; then
            SUCCESS=$((SUCCESS + 1))
        else
            FAILED=$((FAILED + 1))
        fi
    fi
done

echo ""
echo "🖼️  Processing Generated Images..."
echo "-----------------------------------"
for img in attached_assets/generated_images/*.png; do
    if [ -f "$img" ]; then
        TOTAL=$((TOTAL + 1))
        if upscale_image "$img"; then
            SUCCESS=$((SUCCESS + 1))
        else
            FAILED=$((FAILED + 1))
        fi
    fi
done

echo ""
echo "======================================================"
echo "📊 Summary:"
echo "   Total images: $TOTAL"
echo "   ✅ Successfully upscaled: $SUCCESS"
echo "   ❌ Failed: $FAILED"
echo "   💾 Backups saved to: $BACKUP_DIR"
echo ""
echo "✨ Image optimization complete!"
