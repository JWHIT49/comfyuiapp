import Constants from 'expo-constants';

/**
 * Base URL of the backend proxy (the FastAPI service in ../backend).
 *
 * Set this to your PC's LAN IP so a physical iPhone running Expo Go can reach
 * it — "localhost" would point at the phone itself, not your computer.
 * Find the IP with `ipconfig` (IPv4 Address), e.g. http://192.168.1.100:8000
 *
 * You can override it without editing code by changing `extra.apiBaseUrl`
 * in app.json.
 */
export const API_BASE_URL =
  Constants.expoConfig?.extra?.apiBaseUrl ?? 'http://192.168.1.100:8000';

// How often to poll the backend for job progress, in milliseconds.
export const POLL_INTERVAL_MS = 1500;

// A few ready-made instructions to make the app feel alive on first run.
export const PROMPT_SUGGESTIONS = [
  'Give him a hat',
  'Remove his shoes',
  'Add sunglasses',
  'Change the background to a beach',
  'Make it look like winter',
];
