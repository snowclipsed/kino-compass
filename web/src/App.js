import React, { useState, useEffect } from 'react';
import ApiKeyInput from './components/ApiKeyInput';
import ProviderSelection from './components/ProviderSelection';
import SubmitApiButton from './components/SubmitApiButton';
import LlamaCppButton from './components/LlamaCppButton';

function App() {
  const [apiKey, setApiKey] = useState('');
  const [provider, setProvider] = useState('');
  const [message, setMessage] = useState('');
  const [hasApiKey, setHasApiKey] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const checkApiKey = async () => {
      try {
        const response = await fetch('http://localhost:8000/check-api-key');
        const data = await response.json();
        setHasApiKey(data.has_api_key);
      } catch (error) {
        console.error('Error checking API key:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkApiKey();
  }, []);


  const handleSubmit = async() => {
    try {
      const response = await fetch('http://localhost:8000/update-env', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ api_key: apiKey, provider: provider }),
      });

// TODO: Check if entered API key is valid or not.

      const data = await response.json();
      setMessage(data.message || 'Updated successfully');
    } catch (error) {
      setMessage('Error updating environment variables');
      console.error('Error:', error);
    }    
  };


  const handleLlamaCpp = async() => {
    try {
      const response = await fetch('http://localhost:8000/update-env', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ api_key: "", provider: "llamacpp" }),
      });

      const data = await response.json();
      setMessage(data.message || 'Updated successfully');
    } catch (error) {
      setMessage('Error updating environment variables');
      console.error('Error:', error);
    }    
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
      <h1 className="text-4xl font-bold mb-8"> 𝕏 Compass</h1>
      
      <div className="w-full max-w-md space-y-2">
        <ApiKeyInput apiKey={apiKey} setApiKey={setApiKey} />
        <ProviderSelection provider={provider} setProvider={setProvider} />
        <SubmitApiButton onClick={handleSubmit} />
        <h3 class="flex items-center w-full p-2">
          <div class="flex-grow bg-gray-600 rounded h-0.5"></div>
          <span class="mx-3 text-lg font-medium">OR</span>
          <div class="flex-grow bg-gray-600 rounded h-0.5"></div>
        </h3>
        <LlamaCppButton onClick={handleLlamaCpp} />
       {message && <p className="mt-4 text-center">{message}</p>}
      </div>

    </div>
  );
}

export default App;
