const ApiKeyInput = ({ apiKey, setApiKey }) => {
  return (
    <div>
      <label htmlFor="api-key" className="block text-sm font-medium mb-2">
        Enter your LLM API Key
      </label>
      <input
        type="password"
        id="api-key"
        value={apiKey}
        onChange={(e) => setApiKey(e.target.value)}
        className="w-full px-3 py-2 bg-white border border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Your API Key"
      />
    </div>
  );
};

export default ApiKeyInput;
