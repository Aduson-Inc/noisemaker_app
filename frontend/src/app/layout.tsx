import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'NOiSEMaKER - Get Heard. Get Booked. Get Legendary.',
  description: 'The must-have tool for musicians ready to skyrocket growth & stream counts. Automated social media promotion across 8 platforms.',
  keywords: ['music promotion', 'indie artists', 'social media marketing', 'spotify promotion', 'musician tools'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Cormorant+Garamond:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
