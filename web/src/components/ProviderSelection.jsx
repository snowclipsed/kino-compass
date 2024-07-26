const ProviderSelection = ({ provider, setProvider }) => {
  return (
    <div>
      <label htmlFor="provider" className="block text-sm font-medium mb-2">
        Select API Key Provider
      </label>
      <select
        id="provider"
        value={provider}
        onChange={(e) => setProvider(e.target.value)}
        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">Select a provider</option>
        <option value="option1">Groq</option>
        <option value="option2">GPT4o</option>
      </select>
    </div>
  );
};

export default ProviderSelection;