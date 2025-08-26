export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-blue-900">Het Nieuws</h1>
          <p className="text-gray-600 mt-2">Uw dagelijkse nieuwsupdate</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Hero Section */}
        <section className="mb-12">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Hoofdartikel</h2>
            <div className="aspect-video bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
              <span className="text-gray-500">Afbeelding placeholder</span>
            </div>
            <h3 className="text-xl font-semibold mb-2">
              Welkom bij Het Nieuws App
            </h3>
            <p className="text-gray-700 mb-4">
              Dit is uw nieuwe nieuwsapplicatie gebouwd met Next.js en TypeScript. 
              Hier kunt u de laatste nieuwsartikelen, updates en belangrijk nieuws vinden.
            </p>
            <a href="#" className="text-blue-600 hover:text-blue-800 font-medium">
              Lees meer →
            </a>
          </div>
        </section>

        {/* News Grid */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Laatste Nieuws</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* News Card 1 */}
            <article className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="aspect-video bg-gray-200 flex items-center justify-center">
                <span className="text-gray-500">Nieuws foto</span>
              </div>
              <div className="p-4">
                <h3 className="font-semibold text-lg mb-2">Lokaal Nieuws Update</h3>
                <p className="text-gray-600 text-sm mb-2">
                  Korte samenvatting van het nieuwsartikel dat hier zou staan...
                </p>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500">2 uur geleden</span>
                  <a href="#" className="text-blue-600 hover:text-blue-800 text-sm">
                    Lees meer
                  </a>
                </div>
              </div>
            </article>

            {/* News Card 2 */}
            <article className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="aspect-video bg-gray-200 flex items-center justify-center">
                <span className="text-gray-500">Nieuws foto</span>
              </div>
              <div className="p-4">
                <h3 className="font-semibold text-lg mb-2">Technologie Update</h3>
                <p className="text-gray-600 text-sm mb-2">
                  Laatste ontwikkelingen in de technologie sector...
                </p>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500">4 uur geleden</span>
                  <a href="#" className="text-blue-600 hover:text-blue-800 text-sm">
                    Lees meer
                  </a>
                </div>
              </div>
            </article>

            {/* News Card 3 */}
            <article className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="aspect-video bg-gray-200 flex items-center justify-center">
                <span className="text-gray-500">Nieuws foto</span>
              </div>
              <div className="p-4">
                <h3 className="font-semibold text-lg mb-2">Sport Nieuws</h3>
                <p className="text-gray-600 text-sm mb-2">
                  Overzicht van de laatste sportuitslagen en gebeurtenissen...
                </p>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500">6 uur geleden</span>
                  <a href="#" className="text-blue-600 hover:text-blue-800 text-sm">
                    Lees meer
                  </a>
                </div>
              </div>
            </article>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-16">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center">
            <h3 className="text-lg font-semibold mb-2">Het Nieuws</h3>
            <p className="text-gray-400">© 2025 Het Nieuws App. Alle rechten voorbehouden.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
