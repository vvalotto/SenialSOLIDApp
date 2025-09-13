const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  
  return {
    entry: {
      main: './01_presentacion/webapp/static/js/main.js',
      styles: './01_presentacion/webapp/static/css/styles.css'
    },
    output: {
      path: path.resolve(__dirname, '01_presentacion/webapp/static/dist'),
      filename: isProduction ? '[name].[contenthash:8].min.js' : '[name].js',
      publicPath: '/static/dist/',
      clean: true,
    },
    module: {
      rules: [
        {
          test: /\.js$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
            options: {
              presets: ['@babel/preset-env']
            }
          }
        },
        {
          test: /\.css$/,
          use: [
            isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
            'css-loader'
          ]
        },
        {
          test: /\.(png|jpg|jpeg|gif|svg|webp|avif)$/,
          type: 'asset/resource',
          generator: {
            filename: 'images/[name].[contenthash:8][ext]'
          }
        },
        {
          test: /\.(woff|woff2|eot|ttf|otf)$/,
          type: 'asset/resource',
          generator: {
            filename: 'fonts/[name].[contenthash:8][ext]'
          }
        }
      ]
    },
    plugins: [
      new MiniCssExtractPlugin({
        filename: isProduction ? '[name].[contenthash:8].min.css' : '[name].css'
      }),
      ...(isProduction ? [
        new CompressionPlugin({
          algorithm: 'gzip',
          test: /\.(js|css|html|svg)$/,
          threshold: 8192,
          minRatio: 0.8
        }),
        new CompressionPlugin({
          algorithm: 'brotliCompress',
          filename: '[path][base].br',
          test: /\.(js|css|html|svg)$/,
          compressionOptions: {
            level: 11,
          },
          threshold: 8192,
          minRatio: 0.8
        })
      ] : [])
    ],
    optimization: {
      minimize: isProduction,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            compress: {
              drop_console: isProduction,
              drop_debugger: isProduction
            }
          }
        }),
        new CssMinimizerPlugin()
      ],
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            priority: 10,
            reuseExistingChunk: true
          },
          bootstrap: {
            test: /[\\/]node_modules[\\/]bootstrap[\\/]/,
            name: 'bootstrap',
            chunks: 'all',
            priority: 20
          }
        }
      }
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '01_presentacion/webapp/static')
      }
    },
    devServer: {
      static: {
        directory: path.join(__dirname, '01_presentacion/webapp/static'),
      },
      compress: true,
      port: 3000,
      hot: true,
      proxy: {
        '/': 'http://localhost:5000'
      }
    },
    performance: {
      hints: isProduction ? 'warning' : false,
      maxAssetSize: 250000,
      maxEntrypointSize: 250000
    }
  };
};