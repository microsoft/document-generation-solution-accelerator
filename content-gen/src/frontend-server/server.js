const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

// Backend API URL (ACI private IP in VNet)
const BACKEND_URL = process.env.BACKEND_URL || 'http://10.0.4.4:8000';

// Proxy API requests to backend
app.use('/api', createProxyMiddleware({
    target: BACKEND_URL,
    changeOrigin: true,
    pathRewrite: {
        '^/api': '/api'
    },
    // Increase timeout for long-running requests (5 minutes)
    proxyTimeout: 300000,
    timeout: 300000,
    // Support streaming responses (SSE)
    onProxyRes: (proxyRes, req, res) => {
        // Disable buffering for streaming responses
        if (proxyRes.headers['content-type']?.includes('text/event-stream')) {
            res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
            res.setHeader('X-Accel-Buffering', 'no');
            res.flushHeaders();
        }
    },
    onError: (err, req, res) => {
        console.error('Proxy error:', err);
        if (!res.headersSent) {
            res.status(502).json({ error: 'Backend service unavailable' });
        }
    }
}));

// Serve static files from the build directory
app.use(express.static(path.join(__dirname, 'static')));

// Serve index.html for all other routes (SPA support)
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'static', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Frontend server running on port ${PORT}`);
    console.log(`Proxying API requests to ${BACKEND_URL}`);
});
