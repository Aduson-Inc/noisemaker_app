/**
 * SSM Parameter Store Loader for Frontend
 * Fetches OAuth and other credentials from AWS Parameter Store
 * Mirrors the backend's environment_loader.py pattern
 *
 * All secrets are stored under /noisemaker/ path
 */

import { SSMClient, GetParameterCommand, GetParametersByPathCommand } from '@aws-sdk/client-ssm';

const BASE_PATH = '/noisemaker';
const REGION = 'us-east-2';

// Cache for parameters to avoid repeated calls
const parameterCache: Map<string, string> = new Map();
let cacheInitialized = false;

// SSM Client configuration - uses IAM role when no explicit credentials
const ssmConfig: any = {
  region: REGION,
};

// Only set explicit credentials if both are provided
// Otherwise, fall back to IAM role (Amplify execution role)
if (process.env.AWS_ACCESS_KEY_ID && process.env.AWS_SECRET_ACCESS_KEY) {
  ssmConfig.credentials = {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  };
}

const ssmClient = new SSMClient(ssmConfig);

/**
 * Get a single parameter from Parameter Store
 */
export async function getParameter(key: string, defaultValue: string = ''): Promise<string> {
  // Check cache first
  if (parameterCache.has(key)) {
    return parameterCache.get(key) || defaultValue;
  }

  try {
    const command = new GetParameterCommand({
      Name: `${BASE_PATH}/${key}`,
      WithDecryption: true,
    });

    const response = await ssmClient.send(command);
    const value = response.Parameter?.Value || defaultValue;

    // Cache the value
    parameterCache.set(key, value);
    console.log(`[SSM Loader] Retrieved parameter: ${key}`);

    return value;
  } catch (error: any) {
    if (error.name === 'ParameterNotFound') {
      console.warn(`[SSM Loader] Parameter not found: ${key}, using default`);
    } else {
      console.error(`[SSM Loader] Error getting ${key}:`, error.message);
    }
    return defaultValue;
  }
}

/**
 * Get all parameters under /noisemaker/ path
 * Useful for initializing all credentials at once
 */
export async function getAllParameters(): Promise<Map<string, string>> {
  if (cacheInitialized) {
    return parameterCache;
  }

  try {
    const command = new GetParametersByPathCommand({
      Path: BASE_PATH,
      Recursive: true,
      WithDecryption: true,
    });

    const response = await ssmClient.send(command);

    if (response.Parameters) {
      for (const param of response.Parameters) {
        if (param.Name && param.Value) {
          const key = param.Name.replace(`${BASE_PATH}/`, '');
          parameterCache.set(key, param.Value);
        }
      }
    }

    cacheInitialized = true;
    console.log(`[SSM Loader] Retrieved ${parameterCache.size} parameters`);

    return parameterCache;
  } catch (error: any) {
    console.error('[SSM Loader] Error getting all parameters:', error.message);
    return parameterCache;
  }
}

/**
 * OAuth credentials interface
 */
export interface OAuthCredentials {
  google: {
    clientId: string;
    clientSecret: string;
  };
  facebook: {
    clientId: string;
    clientSecret: string;
  };
}

/**
 * NextAuth configuration interface
 */
export interface NextAuthConfig {
  secret: string;
  url: string;
}

/**
 * Get OAuth credentials for Google and Facebook
 */
export async function getOAuthCredentials(): Promise<OAuthCredentials> {
  // Pre-fetch all parameters for efficiency
  await getAllParameters();

  return {
    google: {
      clientId: parameterCache.get('google_client_id') || '',
      clientSecret: parameterCache.get('google_client_secret') || '',
    },
    facebook: {
      clientId: parameterCache.get('facebook_client_id') || '',
      clientSecret: parameterCache.get('facebook_client_secret') || '',
    },
  };
}

/**
 * Get NextAuth configuration
 */
export async function getNextAuthConfig(): Promise<NextAuthConfig> {
  // Pre-fetch all parameters for efficiency
  await getAllParameters();

  return {
    secret: parameterCache.get('nextauth_secret') || parameterCache.get('jwt_secret_key') || '',
    url: parameterCache.get('nextauth_url') || 'https://noisemaker.doowopp.com',
  };
}

/**
 * Initialize all OAuth-related parameters
 * Call this once at app startup for best performance
 */
export async function initializeOAuthParams(): Promise<{
  oauth: OAuthCredentials;
  nextauth: NextAuthConfig;
}> {
  await getAllParameters();

  const oauth = await getOAuthCredentials();
  const nextauth = await getNextAuthConfig();

  // Log status (without exposing secrets)
  console.log('[SSM Loader] OAuth initialization complete:');
  console.log(`  - Google Client ID: ${oauth.google.clientId ? 'SET' : 'MISSING'}`);
  console.log(`  - Google Client Secret: ${oauth.google.clientSecret ? 'SET' : 'MISSING'}`);
  console.log(`  - Facebook Client ID: ${oauth.facebook.clientId ? 'SET' : 'MISSING'}`);
  console.log(`  - Facebook Client Secret: ${oauth.facebook.clientSecret ? 'SET' : 'MISSING'}`);
  console.log(`  - NextAuth Secret: ${nextauth.secret ? 'SET' : 'MISSING'}`);
  console.log(`  - NextAuth URL: ${nextauth.url}`);

  return { oauth, nextauth };
}

/**
 * Clear the parameter cache
 */
export function clearCache(): void {
  parameterCache.clear();
  cacheInitialized = false;
  console.log('[SSM Loader] Cache cleared');
}
