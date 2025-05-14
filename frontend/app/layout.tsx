import type { Metadata } from "next";
import { IBM_Plex_Mono } from 'next/font/google';
import './globals.css';



import dynamic from "next/dynamic";

const MatrixBackground = dynamic(
  () => import('@/components/MatrixBackground'),
  { ssr: true }
);

export const metadata: Metadata = {
  title: "PyFinder",
};



const ibmPlexMono = IBM_Plex_Mono({
  weight: ['400', '700'],
  subsets: ['latin'],
  variable: '--font-mono',
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${ibmPlexMono.variable}`}>
      <body className="font-mono bg-black text-green-400">
        <MatrixBackground />
        {children}
      </body>
    </html>
  );
}