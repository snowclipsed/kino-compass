import React, { useState } from 'react';
import ApiKeyInput from './components/ApiKeyInput';
import ProviderSelection from './components/ProviderSelection';
import SubmitApiButton from './components/SubmitApiButton';

function App() {
  const [apiKey, setApiKey] = useState('');
  const [provider, setProvider] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async() => {
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
    } catch (error) {
      setMessage('Error updating environment variables');
      console.error('Error:', error);
    }    
  };

// TODO: Check if entered API key is valid or not.

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
      <h1 className="text-4xl font-bold mb-8"> 𝕏 Compass</h1>
      
      <div className="w-full max-w-md space-y-6">
        <ApiKeyInput apiKey={apiKey} setApiKey={setApiKey} />
        <ProviderSelection provider={provider} setProvider={setProvider} />
        <SubmitApiButton onClick={handleSubmit} />
        {message && <p className='text-white'>{message}</p>}
      </div>
    </div>
  );
}

export default App;