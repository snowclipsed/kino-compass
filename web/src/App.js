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
    if (!provider) {
      setMessage('Please select a provider');
      return;
    }

    if (['groq', 'gpt4o'].includes(provider) && !apiKey) {
      setMessage('Please enter an API key');
      return;
    }

    try {
      let endpoint, body;

      if (provider === 'llama_cpp') {
        endpoint = 'http://localhost:8000/load-model';
        body = { provider };
      } else {
        endpoint = 'http://localhost:8000/update-env';
        body = { api_key: apiKey, provider };
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const rawResponse = await response.text();
      console.log('Raw response:', rawResponse);

      let data;
      try {
        data = JSON.parse(rawResponse);
      } catch (parseError) {
        console.error('Error parsing JSON:', parseError);
        setMessage('Error: Received invalid response from server');
        return;
      }

      setMessage(data.message || `Launched ${provider} successfully`);
      setIsLaunched(true);
    } catch (error) {
      console.error('Error:', error);
      setMessage(`Error launching ${provider}: ${error.message}`);
    }
  };

  const handleReload = () => {
    window.location.reload();
  };

  useEffect(() => {
    return () => {
      // Reset the state on unmount
      fetch('http://localhost:8000/reset', {
        method: 'POST',
      }).then(response => response.json())
        .then(data => console.log(data.message))
        .catch(error => console.error('Error resetting state:', error));
    };
  }, []);

  if (isLaunched) {
    return <XCompass provider={provider} />;
  }

  return (
    <div className="min-h-screen bg-white text-black flex flex-col items-center justify-center p-4">
      <h1 className="text-4xl font-bold mb-8 cursor-pointer" onClick={handleReload}>𝕏 Compass</h1>
      <div className="w-full max-w-md space-y-6">
        <ProviderSelection provider={provider} setProvider={setProvider} />
        {['groq', 'gpt4o'].includes(provider) && (
          <ApiKeyInput apiKey={apiKey} setApiKey={setApiKey} />
        )}
        <button
          onClick={handleLaunch}
          className="w-full bg-[#1DA1F2] text-white py-2 px-4 rounded hover:bg-blue-700 transition duration-300"
        >
          Launch
        </button>
        {message && <p className="mt-4 text-center">{message}</p>}
      </div>
    </div>
  );
}

export default App;

