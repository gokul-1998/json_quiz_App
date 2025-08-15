const About = () => {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">About Quiz App</h1>
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="mb-4">
          Welcome to Quiz App! This platform is designed to help you test and improve
          your knowledge across various topics.
        </p>
        <p className="mb-4">
          Features:
        </p>
        <ul className="list-disc list-inside mb-4">
          <li>Multiple quiz categories</li>
          <li>Track your progress</li>
          <li>Compete with others</li>
          <li>Create your own quizzes</li>
        </ul>
        <p>
          Get started by logging in with your Google account and exploring our
          collection of quizzes!
        </p>
      </div>
    </div>
  );
};

export default About;
