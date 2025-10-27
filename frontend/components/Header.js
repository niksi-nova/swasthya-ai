export default function Header(){ 
  return (
    <header className="w-full bg-white border-b">
      <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold">H</div>
          <div className="font-semibold">HealthLLM</div>
        </div>
        <nav className="hidden sm:flex space-x-4">
          <a className="text-sm hover:underline" href="/">Home</a>
          <a className="text-sm hover:underline" href="/dashboard">Dashboard</a>
          <a className="text-sm hover:underline" href="/upload">Upload</a>
        </nav>
        <div className="sm:hidden">
          {/* Mobile menu placeholder */}
        </div>
      </div>
    </header>
  )
}
