const Profile = ({ user }) => {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Profile</h1>
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            {user.picture ? (
              <img
                src={user.picture}
                alt={user.name}
                className="rounded-full w-32 h-32 mx-auto mb-4"
              />
            ) : (
              <div className="rounded-full w-32 h-32 mx-auto mb-4 bg-gray-200 flex items-center justify-center">
                <span className="text-4xl font-bold text-gray-700">
                  {user.name.charAt(0).toUpperCase()}
                </span>
              </div>
            )}
            <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
              Edit Profile
            </button>
          </div>
          
          <div className="md:col-span-2">
            <div className="space-y-4">
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Name
                </label>
                <p className="text-gray-900">{user.name}</p>
              </div>
              
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Email
                </label>
                <p className="text-gray-900">{user.email}</p>
              </div>
              
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Member Since
                </label>
                <p className="text-gray-900">
                  {new Date(user.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
