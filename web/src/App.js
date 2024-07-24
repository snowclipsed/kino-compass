import React, { useState } from 'react';
import { runScript } from './api';

function App() {
    const [result, setResult] = useState(null);

    const handleRunScript = async () => {
        try {
            const response = await runScript();
            setResult(response.result);
        } catch (error) {
            console.error('Error:', error);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
            <header className="text-center">
                <h1 className="text-4xl font-bold mb-4">Run Python Script</h1>
                <button
                    onClick={handleRunScript}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700"
                >
                    Run Script
                </button>
                {result && <p className="mt-4 text-lg">Result: {result}</p>}
            </header>
        </div>
    );
}

export default App;
