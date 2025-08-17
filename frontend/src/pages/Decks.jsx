import { useState, useEffect } from 'react';

const Decks = () => {
  const [decks, setDecks] = useState([]);
  const [selectedDeck, setSelectedDeck] = useState(null);
  const [cards, setCards] = useState([]);
  const [modules, setModules] = useState([]);
  const [collaborators, setCollaborators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showCardForm, setShowCardForm] = useState(false);
  const [showModuleForm, setShowModuleForm] = useState(false);
  const [showCollaboratorForm, setShowCollaboratorForm] = useState(false);
  const [editingModule, setEditingModule] = useState(null);
  const [selectedModule, setSelectedModule] = useState(null);
  const [moduleContents, setModuleContents] = useState([]);
  const [showContentForm, setShowContentForm] = useState(false);
  const [editingContent, setEditingContent] = useState(null);
  const [newContent, setNewContent] = useState({
      content_type: 'TEXT',
      content_data: '',
      order: 0
    });
    const [pdfFile, setPdfFile] = useState(null);
    const [textContent, setTextContent] = useState('');
    const [youtubeUrl, setYoutubeUrl] = useState('');
    const [showPreview, setShowPreview] = useState(false);
    const [previewContent, setPreviewContent] = useState(null);
    const [pdfBlobUrl, setPdfBlobUrl] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [showQuestionForm, setShowQuestionForm] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState(null);
  const [newQuestion, setNewQuestion] = useState({
    question_type: 'MCQ',
    question_text: '',
    options: '',
    correct_answer: '',
    order: 0
  });
  const [newDeck, setNewDeck] = useState({
    title: '',
    description: '',
    visibility: 'private'
  });
  const [newCard, setNewCard] = useState({
    front_content: '',
    back_content: ''
  });
  const [newModule, setNewModule] = useState({
    title: '',
    description: ''
  });
  const [newCollaborator, setNewCollaborator] = useState({
    user_id: ''
  });

  useEffect(() => {
    fetchDecks();
  }, []);

  // Clean up blob URL when component unmounts
  useEffect(() => {
    return () => {
      if (pdfBlobUrl) {
        URL.revokeObjectURL(pdfBlobUrl);
      }
    };
  }, [pdfBlobUrl]);

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

  const fetchModules = async (deckId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8001/decks/${deckId}/modules`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setModules(data);
      } else {
        setError('Failed to fetch modules');
      }
    } catch (err) {
      setError('Error fetching modules');
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
    await fetchModules(deck.id);
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

  const handleCreateModule = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newModule)
      });
      
      if (response.ok) {
        const createdModule = await response.json();
        setModules([...modules, createdModule]);
        setNewModule({ title: '', description: '' });
        setShowModuleForm(false);
      } else {
        setError('Failed to create module');
      }
    } catch (err) {
      setError('Error creating module');
    }
  };

  const handleUpdateModule = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${editingModule.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: newModule.title,
          description: newModule.description
        })
      });
      
      if (response.ok) {
        const updatedModule = await response.json();
        setModules(modules.map(m => m.id === updatedModule.id ? updatedModule : m));
        setNewModule({ title: '', description: '' });
        setEditingModule(null);
        setShowModuleForm(false);
      } else {
        setError('Failed to update module');
      }
    } catch (err) {
      setError('Error updating module');
    }
  };

  const handleDeleteModule = async (moduleId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${moduleId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        setModules(modules.filter(m => m.id !== moduleId));
      } else {
        setError('Failed to delete module');
      }
    } catch (err) {
      setError('Error deleting module');
    }
  };

  const fetchModuleContents = async (moduleId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${moduleId}/contents`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setModuleContents(data);
      } else {
        setError('Failed to fetch module contents');
      }
    } catch (err) {
      setError('Error fetching module contents');
    }
  };

  const handleCreateContent = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      
      // Handle different content types
      if (newContent.content_type === 'PDF' && pdfFile) {
        // Handle PDF file upload
        const formData = new FormData();
        formData.append('file', pdfFile);
        
        const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${selectedModule.id}/contents/pdf`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        });
        
        if (response.ok) {
          const createdContent = await response.json();
          setModuleContents([...moduleContents, createdContent]);
          setNewContent({ content_type: 'TEXT', content_data: '', order: 0 });
          setPdfFile(null);
          setShowContentForm(false);
        } else {
          setError('Failed to upload PDF');
        }
      } else if (newContent.content_type === 'TEXT' && textContent) {
        // Handle text to PDF conversion
        const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${selectedModule.id}/contents/text-to-pdf`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            text: textContent,
            title: 'Generated PDF'
          })
        });
        
        if (response.ok) {
          const createdContent = await response.json();
          setModuleContents([...moduleContents, createdContent]);
          setNewContent({ content_type: 'TEXT', content_data: '', order: 0 });
          setTextContent('');
          setShowContentForm(false);
        } else {
          setError('Failed to convert text to PDF');
        }
      } else if (newContent.content_type === 'YOUTUBE' && youtubeUrl) {
        // Handle YouTube URL
        const contentData = {
          content_type: 'YOUTUBE',
          content_data: { url: youtubeUrl },
          order: newContent.order
        };
        
        const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${selectedModule.id}/contents`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(contentData)
        });
        
        if (response.ok) {
          const createdContent = await response.json();
          setModuleContents([...moduleContents, createdContent]);
          setNewContent({ content_type: 'TEXT', content_data: '', order: 0 });
          setYoutubeUrl('');
          setShowContentForm(false);
        } else {
          setError('Failed to add YouTube URL');
        }
      } else {
        // Handle regular text content (existing functionality)
        const contentData = {
          content_type: 'TEXT',
          content_data: newContent.content_data,
          order: newContent.order
        };
        
        const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${selectedModule.id}/contents`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(contentData)
        });
        
        if (response.ok) {
          const createdContent = await response.json();
          setModuleContents([...moduleContents, createdContent]);
          setNewContent({ content_type: 'TEXT', content_data: '', order: 0 });
          setShowContentForm(false);
        } else {
          setError('Failed to create content');
        }
      }
    } catch (err) {
      setError('Error creating content: ' + err.message);
    }
  };

  const handleUpdateContent = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      
      // Handle different content types for update
      if (newContent.content_type === 'TEXT') {
        const contentData = {
          content_type: 'TEXT',
          content_data: textContent,
          order: newContent.order
        };
        
        const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${selectedModule.id}/contents/${editingContent.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(contentData)
        });
        
        if (response.ok) {
          const updatedContent = await response.json();
          setModuleContents(moduleContents.map(c => c.id === updatedContent.id ? updatedContent : c));
          setNewContent({ content_type: 'TEXT', content_data: '', order: 0 });
          setTextContent('');
          setEditingContent(null);
          setShowContentForm(false);
        } else {
          setError('Failed to update text content');
        }
      } else if (newContent.content_type === 'YOUTUBE') {
        const contentData = {
          content_type: 'YOUTUBE',
          content_data: { url: youtubeUrl },
          order: newContent.order
        };
        
        const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${selectedModule.id}/contents/${editingContent.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(contentData)
        });
        
        if (response.ok) {
          const updatedContent = await response.json();
          setModuleContents(moduleContents.map(c => c.id === updatedContent.id ? updatedContent : c));
          setNewContent({ content_type: 'TEXT', content_data: '', order: 0 });
          setYoutubeUrl('');
          setEditingContent(null);
          setShowContentForm(false);
        } else {
          setError('Failed to update YouTube URL');
        }
      } else {
        // Handle other content types (PDF, etc.) with existing functionality
        const contentData = {
          content_type: newContent.content_type,
          content_data: newContent.content_type === 'TEXT' ? newContent.content_data : { url: newContent.content_data },
          order: newContent.order
        };
        
        const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${selectedModule.id}/contents/${editingContent.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(contentData)
        });
        
        if (response.ok) {
          const updatedContent = await response.json();
          setModuleContents(moduleContents.map(c => c.id === updatedContent.id ? updatedContent : c));
          setNewContent({ content_type: 'TEXT', content_data: '', order: 0 });
          setEditingContent(null);
          setShowContentForm(false);
        } else {
          setError('Failed to update content');
        }
      }
    } catch (err) {
      setError('Error updating content: ' + err.message);
    }
  };

  const handleDeleteContent = async (contentId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${selectedModule.id}/contents/${contentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        setModuleContents(moduleContents.filter(c => c.id !== contentId));
      } else {
        setError('Failed to delete content');
      }
    } catch (err) {
      setError('Error deleting content');
    }
  };

  const handlePreviewContent = async (contentId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${selectedModule.id}/contents/${contentId}/preview`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPreviewContent(data);
        
        // If it's a PDF, fetch the actual PDF content
        if (data.content_type === 'pdf') {
          const pdfResponse = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${selectedModule.id}/contents/${contentId}/pdf`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          if (pdfResponse.ok) {
            const blob = await pdfResponse.blob();
            const blobUrl = URL.createObjectURL(blob);
            setPdfBlobUrl(blobUrl);
          }
        }
        
        setShowPreview(true);
      } else {
        setError('Failed to preview content');
      }
    } catch (err) {
      setError('Error previewing content: ' + err.message);
    }
  };

  const fetchQuestions = async (moduleId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${moduleId}/questions`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setQuestions(data);
      } else {
        setError('Failed to fetch questions');
      }
    } catch (err) {
      setError('Error fetching questions');
    }
  };

  const handleCreateQuestion = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      const questionData = {
        question_type: newQuestion.question_type,
        question_text: newQuestion.question_text,
        options: newQuestion.options ? JSON.parse(newQuestion.options) : null,
        correct_answer: newQuestion.correct_answer ? JSON.parse(newQuestion.correct_answer) : null,
        order: newQuestion.order
      };
      
      const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${selectedModule.id}/questions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(questionData)
      });
      
      if (response.ok) {
        const createdQuestion = await response.json();
        setQuestions([...questions, createdQuestion]);
        setNewQuestion({ question_type: 'MCQ', question_text: '', options: '', correct_answer: '', order: 0 });
        setShowQuestionForm(false);
      } else {
        setError('Failed to create question');
      }
    } catch (err) {
      setError('Error creating question');
    }
  };

  const handleUpdateQuestion = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      const questionData = {
        question_type: newQuestion.question_type,
        question_text: newQuestion.question_text,
        options: newQuestion.options ? JSON.parse(newQuestion.options) : null,
        correct_answer: newQuestion.correct_answer ? JSON.parse(newQuestion.correct_answer) : null,
        order: newQuestion.order
      };
      
      const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${selectedModule.id}/questions/${editingQuestion.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(questionData)
      });
      
      if (response.ok) {
        const updatedQuestion = await response.json();
        setQuestions(questions.map(q => q.id === updatedQuestion.id ? updatedQuestion : q));
        setNewQuestion({ question_type: 'MCQ', question_text: '', options: '', correct_answer: '', order: 0 });
        setEditingQuestion(null);
        setShowQuestionForm(false);
      } else {
        setError('Failed to update question');
      }
    } catch (err) {
      setError('Error updating question');
    }
  };

  const handleDeleteQuestion = async (questionId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8001/decks/${selectedDeck.id}/modules/${selectedModule.id}/questions/${questionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        setQuestions(questions.filter(q => q.id !== questionId));
      } else {
        setError('Failed to delete question');
      }
    } catch (err) {
      setError('Error deleting question');
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

  const handleModuleInputChange = (e) => {
    const { name, value } = e.target;
    setNewModule(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleContentInputChange = (e) => {
    const { name, value } = e.target;
    setNewContent(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleQuestionInputChange = (e) => {
    const { name, value } = e.target;
    setNewQuestion(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleBackToDecks = () => {
    setSelectedDeck(null);
    setCards([]);
    setModules([]);
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
              onClick={() => setShowModuleForm(!showModuleForm)}
              className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
            >
              {showModuleForm ? 'Cancel' : 'Add Module'}
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

        {showModuleForm && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">{editingModule ? 'Edit Module' : 'Add New Module'}</h2>
            <form onSubmit={editingModule ? handleUpdateModule : handleCreateModule}>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="title">
                  Title
                </label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={newModule.title}
                  onChange={handleModuleInputChange}
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
                  value={newModule.description}
                  onChange={handleModuleInputChange}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  rows="3"
                />
              </div>
              <div className="flex items-center justify-between">
                <button
                  type="submit"
                  className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
                >
                  {editingModule ? 'Update Module' : 'Add Module'}
                </button>
                {editingModule && (
                  <button
                    type="button"
                    onClick={() => {
                      setEditingModule(null);
                      setNewModule({ title: '', description: '' });
                      setShowModuleForm(false);
                    }}
                    className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 ml-2"
                  >
                    Cancel
                  </button>
                )}
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
          <h2 className="text-2xl font-semibold mb-4">Modules</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {modules.length === 0 ? (
              <div className="col-span-full text-center py-8">
                <p className="text-gray-500">No modules found. Add your first module!</p>
              </div>
            ) : (
              modules.map((module) => (
                <div key={module.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                  <div className="p-4 border-b bg-purple-100">
                    <h3 className="text-lg font-semibold">{module.title}</h3>
                    <p className="text-gray-600 mt-2">{module.description || 'No description'}</p>
                  </div>
                  <div className="p-4 flex justify-end space-x-2">
                    <button
                      onClick={() => {
                        setEditingModule(module);
                        setNewModule({
                          title: module.title,
                          description: module.description || ''
                        });
                        setShowModuleForm(true);
                      }}
                      className="bg-yellow-500 text-white px-3 py-1 rounded hover:bg-yellow-600 text-sm"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => {
                        setSelectedModule(module);
                        fetchModuleContents(module.id);
                        fetchQuestions(module.id); // Also fetch questions when selecting a module
                        setShowQuestionForm(false); // Hide question form initially
                      }}
                      className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 text-sm"
                    >
                      Manage
                    </button>
                    <button
                      onClick={() => handleDeleteModule(module.id)}
                      className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600 text-sm"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {selectedModule && (
          <div className="mt-8 border-t pt-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-semibold">Managing Module: {selectedModule.title}</h2>
              <button
                onClick={() => {
                  setSelectedModule(null);
                  setModuleContents([]);
                  setQuestions([]);
                }}
                className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
              >
                Close Module
              </button>
            </div>
            
            {/* Module Content Section */}
            <div className="mb-8">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-semibold">Content</h3>
                <button
                  onClick={() => setShowContentForm(!showContentForm)}
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                >
                  {showContentForm ? 'Cancel' : 'Add Content'}
                </button>
              </div>
  
              {showContentForm && (
                <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                  <h2 className="text-xl font-semibold mb-4">{editingContent ? 'Edit Content' : 'Add New Content'}</h2>
                  <form onSubmit={editingContent ? handleUpdateContent : handleCreateContent}>
                    {/* Content Form Inputs */}
                     <div className="mb-4">
                      <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="content_type">
                        Content Type
                      </label>
                      <select
                        id="content_type"
                        name="content_type"
                        value={newContent.content_type}
                        onChange={handleContentInputChange}
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                      >
                        <option value="TEXT">Text</option>
                        <option value="PDF">PDF</option>
                        <option value="YOUTUBE">YouTube</option>
                      </select>
                    </div>
                    
                    {/* Conditional content input based on type */}
                    {newContent.content_type === 'TEXT' && (
                      <div className="mb-4">
                        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="text_content">
                          Text Content
                        </label>
                        <textarea
                          id="text_content"
                          name="text_content"
                          value={textContent}
                          onChange={(e) => setTextContent(e.target.value)}
                          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                          rows="6"
                          placeholder="Enter your text content here..."
                        />
                      </div>
                    )}
                    
                    {newContent.content_type === 'PDF' && (
                      <div className="mb-4">
                        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="pdf_file">
                          PDF File
                        </label>
                        <input
                          type="file"
                          id="pdf_file"
                          name="pdf_file"
                          accept=".pdf"
                          onChange={(e) => setPdfFile(e.target.files[0])}
                          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        />
                        <p className="text-gray-600 text-xs mt-1">Upload a PDF file</p>
                      </div>
                    )}
                    
                    {newContent.content_type === 'YOUTUBE' && (
                      <div className="mb-4">
                        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="youtube_url">
                          YouTube URL
                        </label>
                        <input
                          type="text"
                          id="youtube_url"
                          name="youtube_url"
                          value={youtubeUrl}
                          onChange={(e) => setYoutubeUrl(e.target.value)}
                          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                          placeholder="https://www.youtube.com/watch?v=..."
                        />
                        <p className="text-gray-600 text-xs mt-1">Enter a valid YouTube URL</p>
                      </div>
                    )}
                    
                    <div className="mb-4">
                      <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="order">
                        Order
                      </label>
                      <input
                        type="number"
                        id="order"
                        name="order"
                        value={newContent.order}
                        onChange={handleContentInputChange}
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <button
                        type="submit"
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                      >
                        {editingContent ? 'Update Content' : 'Add Content'}
                      </button>
                      {editingContent && (
                        <button
                          type="button"
                          onClick={() => {
                            setEditingContent(null);
                            setNewContent({ content_type: 'TEXT', content_data: '', order: 0 });
                            setTextContent('');
                            setPdfFile(null);
                            setYoutubeUrl('');
                            setShowContentForm(false);
                          }}
                          className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 ml-2"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </form>
                </div>
              )}
  
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {moduleContents.length === 0 ? (
                  <div className="col-span-full text-center py-8">
                    <p className="text-gray-500">No content found.</p>
                  </div>
                ) : (
                  moduleContents.map((content) => (
                     <div key={content.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                      <div className="p-4 border-b bg-blue-100">
                        <h3 className="text-lg font-semibold">Type: {content.content_type}</h3>
                        <p className="text-gray-600 mt-2">Order: {content.order}</p>
                      </div>
                      <div className="p-4">
                        {content.content_type === 'TEXT' ? (
                          <p className="text-gray-700">{content.content_data}</p>
                        ) : content.content_type === 'PDF' ? (
                          <div>
                            <p className="text-gray-700">PDF Content</p>
                            {content.content_data.filename && (
                              <p className="text-gray-600 text-sm">File: {content.content_data.filename}</p>
                            )}
                            {content.content_data.size && (
                              <p className="text-gray-600 text-sm">Size: {content.content_data.size} bytes</p>
                            )}
                            <a
                              href={`http://localhost:8001/decks/${selectedDeck.id}/modules/${selectedModule.id}/contents/${content.id}/pdf`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 text-sm mt-2 inline-block"
                            >
                              View PDF
                            </a>
                          </div>
                        ) : content.content_type === 'YOUTUBE' ? (
                          <div>
                            <p className="text-gray-700">YouTube Video</p>
                            <a
                              href={content.content_data.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 text-sm"
                            >
                              {content.content_data.url}
                            </a>
                          </div>
                        ) : (
                          <p className="text-gray-700">Content type: {content.content_type}</p>
                        )}
                      </div>
                      <div className="p-4 flex justify-end space-x-2">
                        <button
                          onClick={() => {
                            setEditingContent(content);
                            setNewContent({
                              content_type: content.content_type,
                              content_data: content.content_type === 'TEXT' ? content.content_data :
                                content.content_type === 'YOUTUBE' ? content.content_data.url : '',
                              order: content.order
                            });
                            // Set the specific content type fields
                            if (content.content_type === 'TEXT') {
                              setTextContent(content.content_data);
                            } else if (content.content_type === 'YOUTUBE') {
                              setYoutubeUrl(content.content_data.url);
                            }
                            setShowContentForm(true);
                          }}
                          className="bg-yellow-500 text-white px-3 py-1 rounded hover:bg-yellow-600 text-sm"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteContent(content.id)}
                          className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600 text-sm"
                        >
                          Delete
                        </button>
                        <button
                          onClick={() => handlePreviewContent(content.id)}
                          className="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600 text-sm"
                        >
                          Preview
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Preview Modal */}
            {showPreview && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                  <div className="p-6">
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-xl font-semibold">Content Preview</h3>
                      <button
                        onClick={() => {
                          setShowPreview(false);
                          setPreviewContent(null);
                          if (pdfBlobUrl) {
                            URL.revokeObjectURL(pdfBlobUrl);
                            setPdfBlobUrl(null);
                          }
                        }}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                      </button>
                    </div>
                    {previewContent && (
                      <div>
                        <p className="text-gray-600 mb-4">Type: {previewContent.content_type}</p>
                        {previewContent.content_type === 'text' && (
                          <div>
                            <p className="text-gray-700">{previewContent.content}</p>
                          </div>
                        )}
                        {previewContent.content_type === 'pdf' && (
                          <div>
                            <p className="text-gray-700">{previewContent.preview}</p>
                            {pdfBlobUrl ? (
                              <iframe
                                src={pdfBlobUrl}
                                title="PDF Preview"
                                width="100%"
                                height="500px"
                                className="mt-4"
                              />
                            ) : (
                              <p className="text-gray-600 mt-2">Loading PDF preview...</p>
                            )}
                          </div>
                        )}
                        {previewContent.content_type === 'youtube' && (
                          <div>
                            <p className="text-gray-700">{previewContent.preview}</p>
                            <a
                              href={previewContent.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 mt-2 inline-block"
                            >
                              Open in YouTube
                            </a>
                          </div>
                        )}
                        {previewContent.content_type === 'unknown' && (
                          <p className="text-gray-700">{previewContent.preview}</p>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Module Questions Section */}
            <div className="mt-8 border-t pt-8">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-semibold">Questions</h3>
                <button
                  onClick={() => setShowQuestionForm(!showQuestionForm)}
                  className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                >
                  {showQuestionForm ? 'Cancel' : 'Add Question'}
                </button>
              </div>

              {showQuestionForm && (
                <div className="bg-white rounded-lg shadow-md p-6 mb-6 mt-4">
                  <h2 className="text-xl font-semibold mb-4">{editingQuestion ? 'Edit Question' : 'Add New Question'}</h2>
                  <form onSubmit={editingQuestion ? handleUpdateQuestion : handleCreateQuestion}>
                    {/* Question Form Inputs */}
                    <div className="mb-4">
                      <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="question_type">
                        Question Type
                      </label>
                      <select
                        id="question_type"
                        name="question_type"
                        value={newQuestion.question_type}
                        onChange={handleQuestionInputChange}
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                      >
                        <option value="MCQ">Multiple Choice</option>
                        <option value="FILL_UP">Fill in the Blank</option>
                        <option value="FLASHCARD">Flashcard</option>
                        <option value="MATCH_THE_FOLLOWING">Match the Following</option>
                      </select>
                    </div>
                    <div className="mb-4">
                      <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="question_text">
                        Question Text
                      </label>
                      <textarea
                        id="question_text"
                        name="question_text"
                        value={newQuestion.question_text}
                        onChange={handleQuestionInputChange}
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        rows="3"
                        required
                      />
                    </div>
                    <div className="mb-4">
                      <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="options">
                        Options (JSON format)
                      </label>
                      <textarea
                        id="options"
                        name="options"
                        value={newQuestion.options}
                        onChange={handleQuestionInputChange}
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        rows="3"
                        placeholder='{"option1": "Option A", "option2": "Option B"}'
                      />
                    </div>
                    <div className="mb-4">
                      <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="correct_answer">
                        Correct Answer (JSON format)
                      </label>
                      <textarea
                        id="correct_answer"
                        name="correct_answer"
                        value={newQuestion.correct_answer}
                        onChange={handleQuestionInputChange}
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        rows="3"
                        placeholder='{"answer": "option2"}'
                      />
                    </div>
                    <div className="mb-4">
                      <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="order">
                        Order
                      </label>
                      <input
                        type="number"
                        id="order"
                        name="order"
                        value={newQuestion.order}
                        onChange={handleQuestionInputChange}
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <button
                        type="submit"
                        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                      >
                        {editingQuestion ? 'Update Question' : 'Add Question'}
                      </button>
                      {editingQuestion && (
                        <button
                          type="button"
                          onClick={() => {
                            setEditingQuestion(null);
                            setNewQuestion({ question_type: 'MCQ', question_text: '', options: '', correct_answer: '', order: 0 });
                            setShowQuestionForm(false);
                          }}
                          className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 ml-2"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </form>
                </div>
              )}
  
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-4">
                {questions.length === 0 ? (
                  <div className="col-span-full text-center py-8">
                    <p className="text-gray-500">No questions found.</p>
                  </div>
                ) : (
                  questions.map((question) => (
                    <div key={question.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                      <div className="p-4 border-b bg-green-100">
                        <h3 className="text-lg font-semibold">Type: {question.question_type}</h3>
                        <p className="text-gray-600 mt-2">Order: {question.order}</p>
                      </div>
                      <div className="p-4">
                        <p className="text-gray-700">{question.question_text}</p>
                        <div className="mt-2">
                          <p className="text-sm text-gray-600">Options:</p>
                          <pre className="text-xs bg-gray-100 p-2 rounded">{JSON.stringify(question.options, null, 2)}</pre>
                        </div>
                        <div className="mt-2">
                          <p className="text-sm text-gray-600">Correct Answer:</p>
                          <pre className="text-xs bg-gray-100 p-2 rounded">{JSON.stringify(question.correct_answer, null, 2)}</pre>
                        </div>
                      </div>
                      <div className="p-4 flex justify-end space-x-2">
                        <button
                          onClick={() => {
                            setEditingQuestion(question);
                            setNewQuestion({
                              question_type: question.question_type,
                              question_text: question.question_text,
                              options: question.options ? JSON.stringify(question.options, null, 2) : '',
                              correct_answer: question.correct_answer ? JSON.stringify(question.correct_answer, null, 2) : '',
                              order: question.order
                            });
                            setShowQuestionForm(true);
                          }}
                          className="bg-yellow-500 text-white px-3 py-1 rounded hover:bg-yellow-600 text-sm"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteQuestion(question.id)}
                          className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600 text-sm"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // FIXED: The JSX for the deck list view must be returned.
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
              <div className={`p-4 ${deck.visibility === 'public' ? 'bg-green-100' : 'bg-blue-100'}`}>
                <h2 className="text-xl font-semibold text-gray-800">{deck.title}</h2>
                <span className={`text-xs font-semibold ${deck.visibility === 'public' ? 'bg-green-200 text-green-800' : 'bg-blue-200 text-blue-800'} px-2 py-1 rounded-full mt-1 inline-block`}>
                  {deck.visibility}
                </span>
              </div>
              <div className="p-4">
                <p className="text-gray-600 mb-4 h-12 overflow-hidden">
                  {deck.description || 'No description'}
                </p>
                <div className="flex justify-between items-center mt-4">
                  <span className="text-sm text-gray-500">
                    Created on {new Date(deck.created_at).toLocaleDateString()}
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