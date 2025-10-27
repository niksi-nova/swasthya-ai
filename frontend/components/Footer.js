export default function Footer(){
  return (
    <footer className="w-full border-t bg-white mt-8">
      <div className="max-w-4xl mx-auto px-4 py-6 text-sm text-gray-600">
        © {new Date().getFullYear()} HealthLLM. All rights reserved.
      </div>
    </footer>
  )
}
