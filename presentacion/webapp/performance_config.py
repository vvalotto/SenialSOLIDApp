"""
Performance optimization configurations for Flask application
SSA-21 Frontend Performance Implementation
"""
from flask import Flask, request, g, jsonify
from functools import wraps
import time
import hashlib
import gzip
import io
from datetime import datetime, timedelta


class PerformanceMiddleware:
    """Middleware for performance optimizations"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize performance middleware"""
        
        # Enable compression
        self.setup_compression(app)
        
        # Setup caching headers
        self.setup_caching(app)
        
        # Setup security headers
        self.setup_security_headers(app)
        
        # Setup performance monitoring
        self.setup_monitoring(app)
        
        # Setup static file optimization
        self.setup_static_optimization(app)
    
    def setup_compression(self, app: Flask):
        """Setup GZIP compression"""
        
        @app.after_request
        def compress_response(response):
            # Only compress if client accepts gzip
            if 'gzip' not in request.headers.get('Accept-Encoding', ''):
                return response
            
            # Only compress text-based responses
            if not response.content_type.startswith(('text/', 'application/json', 'application/javascript')):
                return response
            
            # Skip if already compressed
            if response.headers.get('Content-Encoding'):
                return response
            
            # Skip small responses (overhead not worth it)
            if len(response.data) < 500:
                return response
            
            try:
                # Compress the response
                gzip_buffer = io.BytesIO()
                with gzip.GzipFile(fileobj=gzip_buffer, mode='wb') as gz_file:
                    gz_file.write(response.data)
                
                compressed_data = gzip_buffer.getvalue()
                
                # Only use compressed version if it's actually smaller
                if len(compressed_data) < len(response.data):
                    response.data = compressed_data
                    response.headers['Content-Encoding'] = 'gzip'
                    response.headers['Content-Length'] = len(compressed_data)
                    response.headers['Vary'] = 'Accept-Encoding'
                
            except Exception as e:
                app.logger.warning(f"Compression failed: {e}")
            
            return response
    
    def setup_caching(self, app: Flask):
        """Setup HTTP caching headers"""
        
        @app.after_request
        def add_cache_headers(response):
            # Static assets - long cache
            if request.endpoint == 'static':
                if any(request.path.endswith(ext) for ext in ['.css', '.js', '.ico', '.png', '.jpg', '.gif', '.woff', '.woff2']):
                    # Cache for 1 year with immutable flag for versioned assets
                    if 'min.' in request.path or '.hash.' in request.path:
                        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
                    else:
                        response.headers['Cache-Control'] = 'public, max-age=86400'  # 1 day
                    
                    # Add ETag for validation
                    if response.data:
                        etag = hashlib.md5(response.data).hexdigest()
                        response.headers['ETag'] = f'"{etag}"'
                        
                        # Handle If-None-Match
                        if request.headers.get('If-None-Match') == f'"{etag}"':
                            return '', 304
            
            # API responses - short cache with revalidation
            elif request.path.startswith('/api/'):
                response.headers['Cache-Control'] = 'private, max-age=300, must-revalidate'
            
            # HTML pages - cache with revalidation
            elif response.content_type.startswith('text/html'):
                response.headers['Cache-Control'] = 'private, max-age=0, must-revalidate'
                response.headers['Expires'] = '0'
            
            return response
    
    def setup_security_headers(self, app: Flask):
        """Setup security and performance headers"""
        
        @app.after_request
        def add_security_headers(response):
            # Security headers
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Performance headers
            response.headers['X-DNS-Prefetch-Control'] = 'on'
            
            # Content Security Policy for performance and security
            csp = [
                "default-src 'self'",
                "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net",
                "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net",
                "font-src 'self' cdn.jsdelivr.net",
                "img-src 'self' data: blob:",
                "connect-src 'self'",
                "manifest-src 'self'"
            ]
            response.headers['Content-Security-Policy'] = '; '.join(csp)
            
            return response
    
    def setup_monitoring(self, app: Flask):
        """Setup performance monitoring"""
        
        @app.before_request
        def start_timer():
            g.start_time = time.time()
        
        @app.after_request
        def log_performance(response):
            if hasattr(g, 'start_time'):
                duration = (time.time() - g.start_time) * 1000  # ms
                
                # Add timing header for debugging
                response.headers['X-Response-Time'] = f'{duration:.2f}ms'
                
                # Log slow requests
                if duration > 2000:  # > 2 seconds
                    app.logger.warning(f"Slow request: {request.method} {request.path} took {duration:.2f}ms")
                
                # Store performance metrics (could send to monitoring service)
                if app.debug:
                    print(f"⚡ {request.method} {request.path} - {duration:.2f}ms - {response.status_code}")
            
            return response
    
    def setup_static_optimization(self, app: Flask):
        """Optimize static file serving"""
        
        @app.route('/sw.js')
        def service_worker():
            """Serve service worker with proper headers"""
            from flask import send_from_directory
            response = send_from_directory(app.static_folder, 'sw.js')
            response.headers['Service-Worker-Allowed'] = '/'
            response.headers['Cache-Control'] = 'no-cache'
            return response


def setup_performance_routes(app: Flask):
    """Setup performance-related API endpoints"""
    
    @app.route('/api/performance/vitals', methods=['POST'])
    def log_web_vitals():
        """Log Core Web Vitals from frontend"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'value', 'rating']
            if not all(field in data for field in required_fields):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Log the metric
            app.logger.info(f"Web Vital - {data['name']}: {data['value']}ms ({data['rating']})")
            
            # Could store in database or send to monitoring service
            # store_web_vital(data)
            
            return jsonify({'status': 'success'}), 200
            
        except Exception as e:
            app.logger.error(f"Error logging web vitals: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/performance/metrics')
    def get_performance_metrics():
        """Get current performance metrics"""
        try:
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'server_info': {
                    'version': app.config.get('VERSION', '1.5.0'),
                    'environment': app.config.get('ENV', 'production')
                },
                'targets': {
                    'LCP': 2000,  # ms
                    'FID': 100,   # ms
                    'CLS': 0.1    # score
                }
            }
            
            response = jsonify(metrics)
            response.headers['Cache-Control'] = 'private, max-age=60'  # Cache for 1 minute
            return response
            
        except Exception as e:
            app.logger.error(f"Error getting performance metrics: {e}")
            return jsonify({'error': 'Internal server error'}), 500


def performance_cache(timeout=300):
    """Decorator for caching expensive operations"""
    def decorator(f):
        cache = {}
        
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = hashlib.md5(f"{f.__name__}{str(args)}{str(kwargs)}".encode()).hexdigest()
            
            # Check cache
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < timeout:
                    return result
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            cache[key] = (result, time.time())
            
            # Clean old entries (simple LRU)
            if len(cache) > 100:
                oldest_key = min(cache.keys(), key=lambda k: cache[k][1])
                del cache[oldest_key]
            
            return result
        
        return wrapper
    return decorator


class AssetVersioning:
    """Handle asset versioning for cache busting"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.asset_versions = {}
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize asset versioning"""
        self.load_asset_versions()
        app.jinja_env.globals['asset_url'] = self.asset_url
    
    def load_asset_versions(self):
        """Load asset versions (from webpack manifest or generate)"""
        try:
            # Try to load from webpack manifest.json
            import json
            import os
            
            manifest_path = os.path.join(self.app.static_folder, 'dist', 'manifest.json')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    self.asset_versions = json.load(f)
            else:
                # Generate versions based on file modification time
                self.generate_asset_versions()
                
        except Exception as e:
            self.app.logger.warning(f"Could not load asset versions: {e}")
            self.generate_asset_versions()
    
    def generate_asset_versions(self):
        """Generate asset versions based on file modification time"""
        import os
        import glob
        
        try:
            static_path = self.app.static_folder
            for asset_path in glob.glob(f"{static_path}/**/*.css", recursive=True) + \
                            glob.glob(f"{static_path}/**/*.js", recursive=True):
                
                rel_path = os.path.relpath(asset_path, static_path).replace('\\', '/')
                mtime = int(os.path.getmtime(asset_path))
                self.asset_versions[rel_path] = f"{rel_path}?v={mtime}"
                
        except Exception as e:
            self.app.logger.warning(f"Could not generate asset versions: {e}")
    
    def asset_url(self, filename):
        """Get versioned asset URL"""
        return self.asset_versions.get(filename, filename)


def configure_performance(app: Flask):
    """Main function to configure all performance optimizations"""
    
    # Initialize performance middleware
    PerformanceMiddleware(app)
    
    # Setup asset versioning
    AssetVersioning(app)
    
    # Setup performance routes
    setup_performance_routes(app)
    
    # Configure Flask settings for performance
    if not app.debug:
        app.config.update(
            # Enable template caching
            SEND_FILE_MAX_AGE_DEFAULT=31536000,  # 1 year for static files
            
            # Session configuration
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE='Lax',
            
            # Other optimizations
            JSONIFY_PRETTYPRINT_REGULAR=False,
            JSON_SORT_KEYS=False
        )
    
    app.logger.info("Performance optimizations configured successfully")
    return app