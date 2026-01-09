import { NextAuthOptions } from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';
import FacebookProvider from 'next-auth/providers/facebook';
import { DynamoDBAdapter } from '@auth/dynamodb-adapter';
import { DynamoDBDocument } from '@aws-sdk/lib-dynamodb';
import { DynamoDB } from '@aws-sdk/client-dynamodb';
import { initializeOAuthParams, OAuthCredentials, NextAuthConfig } from './ssm-loader';

// Initialize DynamoDB client
// Uses Amplify's IAM execution role when no explicit credentials provided
const dynamoConfig: any = {
  region: process.env.AWS_REGION || 'us-east-2',
};

// Only set explicit credentials if both are provided
// Otherwise, fall back to IAM role (Amplify execution role)
if (process.env.AWS_ACCESS_KEY_ID && process.env.AWS_SECRET_ACCESS_KEY) {
  dynamoConfig.credentials = {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  };
}

const dynamoClient = new DynamoDB(dynamoConfig);
const dynamoDoc = DynamoDBDocument.from(dynamoClient);

// Cached credentials from SSM
let cachedOAuthCredentials: OAuthCredentials | null = null;
let cachedNextAuthConfig: NextAuthConfig | null = null;
let initializationPromise: Promise<void> | null = null;

/**
 * Initialize OAuth credentials from AWS Parameter Store
 * This is called once and cached for subsequent requests
 */
async function initializeCredentials(): Promise<void> {
  if (cachedOAuthCredentials && cachedNextAuthConfig) {
    return;
  }

  // Prevent multiple simultaneous initializations
  if (initializationPromise) {
    return initializationPromise;
  }

  initializationPromise = (async () => {
    try {
      console.log('[Auth Options] Initializing OAuth credentials from SSM...');
      const { oauth, nextauth } = await initializeOAuthParams();
      cachedOAuthCredentials = oauth;
      cachedNextAuthConfig = nextauth;
      console.log('[Auth Options] OAuth credentials initialized successfully');
    } catch (error) {
      console.error('[Auth Options] Failed to initialize OAuth credentials:', error);
      // Fall back to environment variables if SSM fails
      cachedOAuthCredentials = {
        google: {
          clientId: process.env.GOOGLE_CLIENT_ID || '',
          clientSecret: process.env.GOOGLE_CLIENT_SECRET || '',
        },
        facebook: {
          clientId: process.env.FACEBOOK_CLIENT_ID || '',
          clientSecret: process.env.FACEBOOK_CLIENT_SECRET || '',
        },
      };
      cachedNextAuthConfig = {
        secret: process.env.NEXTAUTH_SECRET || '',
        url: process.env.NEXTAUTH_URL || 'https://noisemaker.doowopp.com',
      };
    }
  })();

  return initializationPromise;
}

/**
 * Build NextAuth options with credentials from SSM Parameter Store
 */
function buildAuthOptions(oauth: OAuthCredentials, nextauth: NextAuthConfig): NextAuthOptions {
  return {
    adapter: DynamoDBAdapter(dynamoDoc, {
      tableName: 'noisemaker-auth',
    }),
    providers: [
      GoogleProvider({
        clientId: oauth.google.clientId,
        clientSecret: oauth.google.clientSecret,
      }),
      FacebookProvider({
        clientId: oauth.facebook.clientId,
        clientSecret: oauth.facebook.clientSecret,
      }),
    ],
    pages: {
      signIn: '/',
      error: '/',
    },
    callbacks: {
      async signIn({ user, account }) {
        // User signed up via OAuth - capture their info for lead generation
        console.log(`[NextAuth] User signed in: ${user.email} via ${account?.provider}`);
        return true;
      },
      async redirect({ url, baseUrl }) {
        // After OAuth signup, redirect to callback page to exchange tokens
        // Callback page will create user in backend and get JWT
        if (url.startsWith(baseUrl)) {
          return `${baseUrl}/auth/oauth-callback`;
        }
        return baseUrl;
      },
      async session({ session, user }) {
        // Add user ID to session
        if (session.user) {
          session.user.id = user.id;

          // Query accounts table to get OAuth provider
          try {
            const accounts = await dynamoDoc.query({
              TableName: 'noisemaker-auth',
              KeyConditionExpression: 'pk = :pk AND begins_with(sk, :sk)',
              ExpressionAttributeValues: {
                ':pk': `USER#${user.id}`,
                ':sk': 'ACCOUNT#',
              },
            });

            // Add provider to session (google, facebook, etc.)
            if (accounts.Items && accounts.Items.length > 0) {
              session.user.provider = accounts.Items[0].provider;
            }
          } catch (error) {
            console.error('[NextAuth] Error fetching provider:', error);
            // Default to google if query fails
            session.user.provider = 'google';
          }
        }
        return session;
      },
    },
    session: {
      strategy: 'database',
      maxAge: 30 * 24 * 60 * 60, // 30 days
    },
    secret: nextauth.secret,
  };
}

/**
 * Get NextAuth options asynchronously
 * Initializes credentials from SSM on first call, then uses cache
 */
export async function getAuthOptions(): Promise<NextAuthOptions> {
  await initializeCredentials();

  if (!cachedOAuthCredentials || !cachedNextAuthConfig) {
    throw new Error('Failed to initialize OAuth credentials');
  }

  return buildAuthOptions(cachedOAuthCredentials, cachedNextAuthConfig);
}

/**
 * Legacy export for backwards compatibility
 * WARNING: This uses synchronous access - credentials must be initialized first
 * Prefer using getAuthOptions() for new code
 */
export const authOptions: NextAuthOptions = {
  adapter: DynamoDBAdapter(dynamoDoc, {
    tableName: 'noisemaker-auth',
  }),
  providers: [
    GoogleProvider({
      // These will be empty until initializeCredentials() is called
      // The route handler should use getAuthOptions() instead
      clientId: process.env.GOOGLE_CLIENT_ID || '',
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || '',
    }),
    FacebookProvider({
      clientId: process.env.FACEBOOK_CLIENT_ID || '',
      clientSecret: process.env.FACEBOOK_CLIENT_SECRET || '',
    }),
  ],
  pages: {
    signIn: '/',
    error: '/',
  },
  callbacks: {
    async signIn({ user, account }) {
      console.log(`[NextAuth] User signed in: ${user.email} via ${account?.provider}`);
      return true;
    },
    async redirect({ url, baseUrl }) {
      if (url.startsWith(baseUrl)) {
        return `${baseUrl}/auth/oauth-callback`;
      }
      return baseUrl;
    },
    async session({ session, user }) {
      if (session.user) {
        session.user.id = user.id;
        try {
          const accounts = await dynamoDoc.query({
            TableName: 'noisemaker-auth',
            KeyConditionExpression: 'pk = :pk AND begins_with(sk, :sk)',
            ExpressionAttributeValues: {
              ':pk': `USER#${user.id}`,
              ':sk': 'ACCOUNT#',
            },
          });
          if (accounts.Items && accounts.Items.length > 0) {
            session.user.provider = accounts.Items[0].provider;
          }
        } catch (error) {
          console.error('[NextAuth] Error fetching provider:', error);
          session.user.provider = 'google';
        }
      }
      return session;
    },
  },
  session: {
    strategy: 'database',
    maxAge: 30 * 24 * 60 * 60,
  },
  secret: process.env.NEXTAUTH_SECRET,
};
