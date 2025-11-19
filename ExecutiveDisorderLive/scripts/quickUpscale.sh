#!/bin/bash
# Quick upscale remaining images only

echo "🚀 Quick Upscale - Remaining Images"
echo "===================================="

TOTAL=0
SUCCESS=0

for img in client/public/characters/ronald-goldenberg.png \
           client/public/characters/senator-tradition.png \
           client/public/characters/tech-disruptor.png \
           client/public/characters/conspiracy-chief.png; do
    
    if [ -f "$img" ]; then
        DIMS=$(identify -format "%wx%h" "$img" 2>/dev/null)
        WIDTH=$(echo $DIMS | cut -d'x' -f1)
        
        # Only upscale if width is less than 1500 (not already upscaled)
        if [ "$WIDTH" -lt "1500" ]; then
            HEIGHT=$(echo $DIMS | cut -d'x' -f2)
            NEW_WIDTH=$((WIDTH * 2))
            NEW_HEIGHT=$((HEIGHT * 2))
            
            echo "📐 Upscaling $img: ${WIDTH}x${HEIGHT} → ${NEW_WIDTH}x${NEW_HEIGHT}"
            
            convert "$img" -filter Lanczos -resize ${NEW_WIDTH}x${NEW_HEIGHT} -quality 85 -strip "${img}.temp"
            if [ $? -eq 0 ]; then
                mv "${img}.temp" "$img"
                echo "✅ Success!"
                SUCCESS=$((SUCCESS + 1))
            fi
            TOTAL=$((TOTAL + 1))
        fi
    fi
done

echo ""
echo "✨ Upscaled $SUCCESS/$TOTAL images"
