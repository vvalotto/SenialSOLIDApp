#!/bin/bash
# SSA-21 Frontend Deployment Script

echo "🚀 Deploying SSA-21 Performance Optimizations..."

# Build assets
echo "📦 Building assets..."
python build_assets.py

# Optimize images
echo "🖼️ Optimizing images..."
python optimize_images.py

# Run performance tests
echo "⚡ Running performance tests..."
python performance_test.py --url ${1:-http://localhost:5000}

echo "✅ Deployment complete!"
