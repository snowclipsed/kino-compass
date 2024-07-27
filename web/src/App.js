import React, { useState, useEffect } from 'react';
import ApiKeyInput from './components/ApiKeyInput';
import ProviderSelection from './components/ProviderSelection';
import XCompass from './components/XCompass.jsx';

function App() {
  const [apiKey, setApiKey] = useState('');
  const [provider, setProvider] = useState('');
  const [message, setMessage] = useState('');
  const [isLaunched, setIsLaunched] = useState(false);

  const handleLaunch = async () => {
    if (provider === 'llama_cpp') {
      setIsLaunched(true);
    } else if (provider === 'groq' || provider === 'gpt4o') {
      if (!apiKey) {
        setMessage('Please enter an API key');
        return;
      }
      try {
        const response = await fetch('http://localhost:8000/update-env', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ api_key: apiKey, provider: provider }),
        });

        const data = await response.json();
        setMessage(data.message || 'Updated successfully');
        setIsLaunched(true);
      } catch (error) {
        setMessage('Error updating environment variables');
        console.error('Error:', error);
      }
    } else {
      setMessage('Please select a provider');
    }
  };

  if (isLaunched) {
    return <XCompass />;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
      <h1 className="text-4xl font-bold mb-8">𝕏 Compass</h1>
      <div className="w-full max-w-md space-y-6">
        <ProviderSelection provider={provider} setProvider={setProvider} />
        {(provider === 'groq' || provider === 'gpt4o') && (
          <ApiKeyInput apiKey={apiKey} setApiKey={setApiKey} />
        )}
        <button 
          onClick={handleLaunch}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition duration-300"
        >
          Launch
        </button>
        
        {message && <p className="mt-4 text-center">{message}</p>}
      </div>
    </div>
  );
}

export default App;
