const Quizzes = () => {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Available Quizzes</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Sample Quiz Cards */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="bg-blue-600 text-white p-4">
            <h2 className="text-xl font-semibold">JavaScript Basics</h2>
          </div>
          <div className="p-4">
            <p className="text-gray-600 mb-4">
              Test your knowledge of JavaScript fundamentals.
            </p>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">10 questions</span>
              <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                Start Quiz
              </button>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="bg-green-600 text-white p-4">
            <h2 className="text-xl font-semibold">Python Basics</h2>
          </div>
          <div className="p-4">
            <p className="text-gray-600 mb-4">
              Learn the fundamentals of Python programming.
            </p>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">15 questions</span>
              <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                Start Quiz
              </button>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="bg-purple-600 text-white p-4">
            <h2 className="text-xl font-semibold">React Fundamentals</h2>
          </div>
          <div className="p-4">
            <p className="text-gray-600 mb-4">
              Test your React.js knowledge.
            </p>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">12 questions</span>
              <button className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700">
                Start Quiz
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Quizzes;
