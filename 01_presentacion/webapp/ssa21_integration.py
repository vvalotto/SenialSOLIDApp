
# SSA-21 Performance Integration
# Add this to your Flask app initialization:

from performance_config import configure_performance

# After creating your Flask app:
app = configure_performance(app)

# This adds:
# - GZIP compression middleware
# - HTTP caching headers
# - Security headers
# - Performance monitoring
# - Asset versioning
# - Core Web Vitals API endpoints
