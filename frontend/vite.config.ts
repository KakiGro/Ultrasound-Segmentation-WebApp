import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: [
      'kaki-jetson.local', // Add your specific hostname here
      '.kakihub.com',    // Or a wildcard for subdomains
      '192.168.1.116'         // Or an IP address
    ],
  },
})
