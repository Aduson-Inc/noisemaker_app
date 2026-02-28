import { SSMClient, GetParameterCommand } from '@aws-sdk/client-ssm';

// Load JWT secret from AWS Parameter Store at startup (same source as backend)
let jwtSecret = '';
try {
  const ssm = new SSMClient({ region: 'us-east-2' });
  const { Parameter } = await ssm.send(
    new GetParameterCommand({
      Name: '/noisemaker/jwt_secret_key',
      WithDecryption: true,
    })
  );
  jwtSecret = Parameter?.Value || '';
  if (jwtSecret) {
    console.log('JWT_SECRET loaded from Parameter Store');
  }
} catch (error) {
  console.warn('Could not load JWT_SECRET from SSM:', error.message);
  console.warn('Protected routes (/dashboard, /onboarding, /milestone) will redirect to /');
}

/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'i.scdn.co',
        pathname: '/image/**',
      },
    ],
  },
  env: {
    JWT_SECRET: jwtSecret,
  },
};

export default nextConfig;
