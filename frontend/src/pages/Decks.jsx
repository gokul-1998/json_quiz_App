import { useState, useEffect } from 'react';

const Decks = () => {
  const [decks, setDecks] = useState([]);
  const [selectedDeck, setSelectedDeck] = useState(null);
  const [cards, setCards] = useState([]);
  const [collaborators, setCollaborators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showCardForm, setShowCardForm] = useState(false);
  const [showCollaboratorForm, setShowCollaboratorForm] = useState(false);
  const [newDeck, setNewDeck] = useState({
    title: '',
    description: '',
    visibility: 'private'
  });
  const [newCard, setNewCard] = useState({
    front_content: '',
    back_content: ''
  });
  const [newCollaborator, setNewCollaborator] = useState({
    user_id: ''
  });

  useEffect(() => {
    fetchDecks();
  }, []);

  const fetchDecks = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8001/decks/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDecks(data);
      } else {
        setError('Failed to fetch decks');
      }
    } catch (err) {
      setError('Error fetching decks');
    } finally {
      setLoading(false);
    }
  };

  const fetchCards = async (deckId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8001/decks/${deckId}/cards`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCards(data);
      } else {
        setError('Failed to fetch cards');
      }
    } catch (err) {
      setError('Error fetching cards');
    }
  };

  const fetchCollaborators = async (deckId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8001/decks/${deckId}/collaborators`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCollaborators(data);
      } else {
        setError('Failed to fetch collaborators');
      }
    } catch (err) {
      setError('Error fetching collaborators');
    }
  };

  const handleCreateDeck = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8001/decks/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newDeck)
      });
      
      if (response.ok) {
        const createdDeck = await response.json();
        setDecks([...decks, createdDeck]);
        setNewDeck({ title: '', description: '', visibility: 'private' });
        setShowCreateForm(false);
      } else {
        setError('Failed to create deck');
      }
    } catch (err) {
      setError('Error creating deck');
    }
  };

  const handleSelectDeck = async (deck) => {
    setSelectedDeck(deck);
    await fetchCards(deck.id);
    await fetchCollaborators(deck.id);
  };

  const handleCreateCard = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/cards`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newCard)
      });
      
      if (response.ok) {
        const createdCard = await response.json();
        setCards([...cards, createdCard]);
        setNewCard({ front_content: '', back_content: '' });
        setShowCardForm(false);
      } else {
        setError('Failed to create card');
      }
    } catch (err) {
      setError('Error creating card');
    }
  };

  const handleAddCollaborator = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/collaborators`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newCollaborator)
      });
      
      if (response.ok) {
        const createdCollaborator = await response.json();
        setCollaborators([...collaborators, createdCollaborator]);
        setNewCollaborator({ user_id: '' });
        setShowCollaboratorForm(false);
      } else {
        setError('Failed to add collaborator');
      }
    } catch (err) {
      setError('Error adding collaborator');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewDeck(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCardInputChange = (e) => {
    const { name, value } = e.target;
    setNewCard(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCollaboratorInputChange = (e) => {
    const { name, value } = e.target;
    setNewCollaborator(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleBackToDecks = () => {
    setSelectedDeck(null);
    setCards([]);
    setCollaborators([]);
  };

  if (loading) {
    return <div className="container mx-auto p-8">Loading decks...</div>;
  }

  if (selectedDeck) {
    return (
      <div className="container mx-auto p-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Deck: {selectedDeck.title}</h1>
          <div className="space-x-2">
            <button
              onClick={handleBackToDecks}
              className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
            >
              Back to Decks
            </button>
            <button
              onClick={() => setShowCardForm(!showCardForm)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              {showCardForm ? 'Cancel' : 'Add Card'}
            </button>
            <button
              onClick={() => setShowCollaboratorForm(!showCollaboratorForm)}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              {showCollaboratorForm ? 'Cancel' : 'Add Collaborator'}
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {showCardForm && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Add New Card</h2>
            <form onSubmit={handleCreateCard}>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="front_content">
                  Front Content
                </label>
                <textarea
                  id="front_content"
                  name="front_content"
                  value={newCard.front_content}
                  onChange={handleCardInputChange}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  rows="3"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="back_content">
                  Back Content
                </label>
                <textarea
                  id="back_content"
                  name="back_content"
                  value={newCard.back_content}
                  onChange={handleCardInputChange}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  rows="3"
                  required
                />
              </div>
              <div className="flex items-center justify-between">
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                >
                  Add Card
                </button>
              </div>
            </form>
          </div>
        )}

        {showCollaboratorForm && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Add Collaborator</h2>
            <form onSubmit={handleAddCollaborator}>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="user_id">
                  User ID
                </label>
                <input
                  type="text"
                  id="user_id"
                  name="user_id"
                  value={newCollaborator.user_id}
                  onChange={handleCollaboratorInputChange}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  required
                />
              </div>
              <div className="flex items-center justify-between">
                <button
                  type="submit"
                  className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                >
                  Add Collaborator
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Collaborators</h2>
          {collaborators.length === 0 ? (
            <p className="text-gray-500">No collaborators found.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {collaborators.map((collaborator) => (
                <div key={collaborator.id} className="bg-white rounded-lg shadow-md p-4">
                  <p className="text-gray-700">User ID: {collaborator.user_id}</p>
                  <p className="text-gray-500 text-sm">Added: {new Date(collaborator.created_at).toLocaleDateString()}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Cards</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {cards.length === 0 ? (
              <div className="col-span-full text-center py-8">
                <p className="text-gray-500">No cards found. Add your first card!</p>
              </div>
            ) : (
              cards.map((card) => (
                <div key={card.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                  <div className="p-4 border-b">
                    <h3 className="text-lg font-semibold">Front</h3>
                    <p className="text-gray-700 mt-2">{card.front_content}</p>
                  </div>
                  <div className="p-4">
                    <h3 className="text-lg font-semibold">Back</h3>
                    <p className="text-gray-700 mt-2">{card.back_content}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Flashcard Decks</h1>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {showCreateForm ? 'Cancel' : 'Create New Deck'}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {showCreateForm && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Create New Deck</h2>
          <form onSubmit={handleCreateDeck}>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="title">
                Title
              </label>
              <input
                type="text"
                id="title"
                name="title"
                value={newDeck.title}
                onChange={handleInputChange}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                required
              />
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="description">
                Description
              </label>
              <textarea
                id="description"
                name="description"
                value={newDeck.description}
                onChange={handleInputChange}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                rows="3"
              />
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="visibility">
                Visibility
              </label>
              <select
                id="visibility"
                name="visibility"
                value={newDeck.visibility}
                onChange={handleInputChange}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              >
                <option value="private">Private</option>
                <option value="public">Public</option>
              </select>
            </div>
            <div className="flex items-center justify-between">
              <button
                type="submit"
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Create Deck
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {decks.length === 0 ? (
          <div className="col-span-full text-center py-8">
            <p className="text-gray-500">No decks found. Create your first deck!</p>
          </div>
        ) : (
          decks.map((deck) => (
            <div key={deck.id} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className={`p-4 ${deck.visibility === 'public' ? 'bg-green-600' : 'bg-blue-600'} text-white`}>
                <h2 className="text-xl font-semibold">{deck.title}</h2>
                <span className="text-xs bg-white bg-opacity-25 px-2 py-1 rounded mt-1 inline-block">
                  {deck.visibility}
                </span>
              </div>
              <div className="p-4">
                <p className="text-gray-600 mb-4">
                  {deck.description || 'No description'}
                </p>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">
                    {deck.cards ? deck.cards.length : 0} cards
                  </span>
                  <button 
                    onClick={() => handleSelectDeck(deck)}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                  >
                    View Deck
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Decks;