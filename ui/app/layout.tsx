import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "@copilotkit/react-core/v2/styles.css";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["300", "400", "500", "600", "700", "800", "900"],
});

export const metadata: Metadata = {
  title: "Substack Author Agent",
  description:
    "Visual content strategy agent for Substack authors — powered by Agno + CopilotKit",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="bg-dark-bg text-white font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
