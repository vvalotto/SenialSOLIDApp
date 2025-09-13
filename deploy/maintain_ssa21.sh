#!/bin/bash
# SSA-21 Maintenance Script

echo "🔧 SSA-21 Performance Maintenance..."

# Clean old assets
echo "🗑️ Cleaning old assets..."
find 01_presentacion/webapp/static/dist -name "*.js" -mtime +30 -delete
find 01_presentacion/webapp/static/dist -name "*.css" -mtime +30 -delete

# Update dependencies
echo "📦 Updating dependencies..."
npm update

# Run performance audit
echo "📊 Performance audit..."
python performance_test.py

echo "✅ Maintenance complete!"
