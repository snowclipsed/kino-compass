import React, { useState } from 'react';
import ApiKeyInput from './components/ApiKeyInput';
import ProviderSelection from './components/ProviderSelection';
import SubmitApiButton from './components/SubmitApiButton';

function App() {
  const [apiKey, setApiKey] = useState('');
  const [provider, setProvider] = useState('');

  const handleSubmit = () => {
    console.log('Submitting:',  { apiKey, provider });
    // Add your submit logic here
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
      <h1 className="text-4xl font-bold mb-8">𝕏 Compass</h1>
      
      <div className="w-full max-w-md space-y-6">
        <ApiKeyInput apiKey={apiKey} setApiKey={setApiKey} />
        <ProviderSelection provider={provider} setProvider={setProvider} />
        <SubmitApiButton onClick={handleSubmit} />
      </div>
    </div>
  );
}

export default App;