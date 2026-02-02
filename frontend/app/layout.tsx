 import "./globals.css";
 
 export const metadata = {
   title: "NeuroGenesis Builder Console",
   description: "Realtime operations console for NeuroGenesis"
 };
 
 export default function RootLayout({
   children
 }: {
   children: React.ReactNode;
 }) {
   return (
     <html lang="en">
       <body>{children}</body>
     </html>
   );
 }
