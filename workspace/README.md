# Het Nieuws App

A modern Dutch news application built with Next.js, TypeScript, and Tailwind CSS.

## Features

- 📰 Clean, responsive news layout
- 🇳🇱 Dutch language interface
- ⚡ Fast performance with Next.js 15 and Turbopack
- 🎨 Modern styling with Tailwind CSS
- 📱 Mobile-friendly responsive design
- 🔍 SEO optimized

## Getting Started

First, install the dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure

```
src/
├── app/
│   ├── globals.css     # Global styles
│   ├── layout.tsx      # Root layout component
│   ├── page.tsx        # Homepage component
│   └── favicon.ico     # App icon
```

## Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build the application for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint for code quality

## Technology Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Bundler**: Turbopack (for development)
- **Linting**: ESLint with Next.js config

## Future Enhancements

- Add news categories and filtering
- Implement news article detail pages
- Add search functionality
- Integrate with news APIs
- Add user preferences and bookmarks
- Implement dark mode
- Add comment system

## Development

The page auto-updates as you edit files. You can start customizing by modifying `src/app/page.tsx`.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about the technologies used:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API
- [Tailwind CSS](https://tailwindcss.com/docs) - utility-first CSS framework
- [TypeScript](https://www.typescriptlang.org/docs/) - typed JavaScript

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out the [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
