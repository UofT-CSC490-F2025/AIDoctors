export function LoadingScreen() {
  return (
    <div className="fixed top-0 left-0 z-50 w-screen h-screen flex items-center justify-center p-4 bg-white">
      <div className="h-16 w-16 rounded-full border-4 border-gray-300 border-t-transparent animate-spin" />
    </div>
  );
}
