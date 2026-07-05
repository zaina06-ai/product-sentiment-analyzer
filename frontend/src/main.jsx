// main.jsx
// Entry point — mounts <App /> into the #root div in index.html.
// Must import index.css here so Tailwind styles are globally available.

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
