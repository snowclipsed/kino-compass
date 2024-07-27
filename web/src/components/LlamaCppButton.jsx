const LlamaCppButton = ({ onClick }) => {
    return (
      <button
        onClick={onClick}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900"
      >
        Launch with Llama.cpp
      </button>
    );
  };
  
  export default LlamaCppButton;
