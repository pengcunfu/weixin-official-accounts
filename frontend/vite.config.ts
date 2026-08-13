import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: false,
    port: 3000,
  },
  preview: {
    port: 3000,
  },
  build: {
    sourcemap: false,
    chunkSizeWarningLimit: 1200,
    rolldownOptions: {
      output: {
        // 按依赖拆分 vendor 包，充分利用浏览器缓存
        codeSplitting: {
          groups: [
            {
              name: 'react-vendor',
              test: /node_modules[\\/](react|react-dom|react-router-dom|scheduler|use-sync-external-store)/,
            },
            {
              name: 'antd',
              test: /node_modules[\\/](antd|@ant-design)/,
            },
            {
              name: 'charts',
              test: /node_modules[\\/](recharts|victory-vendor|d3-|internmap)/,
            },
            {
              name: 'utils',
              test: /node_modules[\\/](axios|dayjs)/,
            },
          ],
        },
      },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.{test,spec}.{js,ts,jsx,tsx}'],
    passWithNoTests: true,
  },
});
