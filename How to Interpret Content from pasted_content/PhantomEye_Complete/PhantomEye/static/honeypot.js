// PhantomEye Honeypot JavaScript - Static Version
// This file serves as a replacement for original JavaScript files

(function() {
    'use strict';
    
    console.log('PhantomEye Honeypot JavaScript Loaded');
    
    // Fake jQuery if not present
    if (typeof $ === 'undefined') {
        window.$ = function(selector) {
            return {
                ready: function(fn) { setTimeout(fn, 100); },
                click: function(fn) { 
                    document.addEventListener('click', fn);
                    return this;
                },
                submit: function(fn) {
                    document.addEventListener('submit', fn);
                    return this;
                },
                val: function() { return ''; },
                text: function() { return ''; },
                hide: function() { return this; },
                show: function() { return this; }
            };
        };
    }
    
    // Fake common JavaScript libraries
    window.React = window.React || {};
    window.Vue = window.Vue || {};
    window.Angular = window.Angular || {};
    
    // Override common functions to prevent errors
    window.fetch = window.fetch || function() {
        return Promise.resolve({
            json: () => Promise.resolve({}),
            text: () => Promise.resolve('')
        });
    };
    
    // Fake analytics
    window.gtag = window.gtag || function() {};
    window.ga = window.ga || function() {};
    window._gaq = window._gaq || [];
    
    // Log all function calls
    const originalConsoleLog = console.log;
    console.log = function(...args) {
        // Send to honeypot logger
        if (window.logInteraction) {
            window.logInteraction('console_log', { args: args });
        }
        originalConsoleLog.apply(console, args);
    };
    
    // Fake AJAX requests
    if (window.XMLHttpRequest) {
        const originalXHR = window.XMLHttpRequest;
        window.XMLHttpRequest = function() {
            const xhr = new originalXHR();
            const originalOpen = xhr.open;
            const originalSend = xhr.send;
            
            xhr.open = function(method, url, ...args) {
                if (window.logInteraction) {
                    window.logInteraction('xhr_request', {
                        method: method,
                        url: url
                    });
                }
                return originalOpen.apply(this, [method, '/honeypot', ...args]);
            };
            
            xhr.send = function(data) {
                if (window.logInteraction) {
                    window.logInteraction('xhr_send', { data: data });
                }
                // Simulate response
                setTimeout(() => {
                    xhr.readyState = 4;
                    xhr.status = 200;
                    xhr.responseText = '{"status":"success"}';
                    if (xhr.onreadystatechange) {
                        xhr.onreadystatechange();
                    }
                }, 500);
            };
            
            return xhr;
        };
    }
    
})();

