#!/bin/bash
# Upscale all generated images in attached_assets

echo "🖼️  Upscaling Generated Images"
echo "=============================="

TOTAL=0
SUCCESS=0
SKIPPED=0

for img in attached_assets/generated_images/*.png; do
    if [ -f "$img" ]; then
        DIMS=$(identify -format "%wx%h" "$img" 2>/dev/null)
        if [ -z "$DIMS" ]; then
            continue
        fi
        
        WIDTH=$(echo $DIMS | cut -d'x' -f1)
        HEIGHT=$(echo $DIMS | cut -d'x' -f2)
        
        # Skip if already high-res (wider than 1500px)
        if [ "$WIDTH" -gt "1500" ]; then
            echo "⏭️  Skipping (already upscaled): $img ($DIMS)"
            SKIPPED=$((SKIPPED + 1))
            continue
        fi
        
        NEW_WIDTH=$((WIDTH * 2))
        NEW_HEIGHT=$((HEIGHT * 2))
        
        echo "📐 Upscaling: $(basename $img) ${WIDTH}x${HEIGHT} → ${NEW_WIDTH}x${NEW_HEIGHT}"
        
        convert "$img" -filter Lanczos -resize ${NEW_WIDTH}x${NEW_HEIGHT} -quality 85 -strip "${img}.temp"
        if [ $? -eq 0 ]; then
            mv "${img}.temp" "$img"
            SUCCESS=$((SUCCESS + 1))
        fi
        TOTAL=$((TOTAL + 1))
    fi
done

echo ""
echo "✨ Summary:"
echo "   Upscaled: $SUCCESS"
echo "   Skipped: $SKIPPED"
echo "   Total processed: $TOTAL"
