import type { CapacitorConfig } from '@capacitor/cli';

const siteUrl = process.env.SITE_URL || 'https://SEU-PROJETO.runsite.app';

const config: CapacitorConfig = {
  appId: 'com.catalogodecor.app',
  appName: 'Catálogo Decor',
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
