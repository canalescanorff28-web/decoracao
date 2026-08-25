import type { CapacitorConfig } from '@capacitor/cli';

const siteUrl = process.env.SITE_URL || 'https://decoracao.runsite.app';

const config: CapacitorConfig = {
  appId: 'com.catalogodecor.app',
  appName: 'Aline & Érika Decor',
  webDir: 'mobile',
  server: {
    url: siteUrl,
    cleartext: false
  },
  android: {
    allowMixedContent: false
  }
};
export default config;
