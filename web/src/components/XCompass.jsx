import React, { useCallback, useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { X, Upload, AlertCircle } from 'lucide-react';

const XCompass = ({ provider }) => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [word, setWord] = useState('');
  const [coords, setCoords] = useState({ x: 0.5, y: 0.5 });
  const [attributes, setAttributes] = useState('');
  const [error, setError] = useState('');
  const [uploadStatus, setUploadStatus] = useState(null);
  const [panelWidth, setPanelWidth] = useState(400);
  const resizeRef = useRef(null);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (resizeRef.current) {
        const newWidth = window.innerWidth - e.clientX;
        setPanelWidth(Math.max(300, Math.min(newWidth, window.innerWidth - 300)));
      }
    };

    const handleMouseUp = () => {
      resizeRef.current = null;
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  const startResize = (e) => {
    e.preventDefault();
    resizeRef.current = true;
  };

  const onDrop = useCallback((acceptedFiles) => {
    const selectedFile = acceptedFiles[0];
    setFile(selectedFile);
    setUploadStatus({
      name: selectedFile.name,
      size: selectedFile.size,
      progress: 0,
      status: 'uploading'
    });
    
    // Start upload process
    handleUpload(selectedFile);
  }, []);

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    onDrop(Array.from(e.dataTransfer.files));
  };

  const handleUpload = async (fileToUpload) => {
    if (!fileToUpload) {
      setMessage('Please select a file first.');
      return;
    }
    const formData = new FormData();
    formData.append('file', fileToUpload);
    try {
      const response = await axios.post('http://localhost:8000/upload-tweets', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadStatus(prev => ({ ...prev, progress: percentCompleted }));
        }
      });
      setMessage(response.data.message);
      setUploadStatus(prev => ({ ...prev, status: 'completed' }));
    } catch (error) {
      console.error("Error uploading file:", error.message);
      setUploadStatus(prev => ({ ...prev, status: 'error' }));
    }
  };

  const fetchCoordinates = useCallback(async () => {
    if (!word || !provider) {
      setError("Please enter a word!");
      return;
    }
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/get-coords', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ word, provider }),
      });
      if (!response.ok) throw new Error('Failed to fetch coordinates');
      const data = await response.json();
      const [x, y] = data.coordinates;
      const normalizedX = (x + 1) / 2;
      const normalizedY = 1 - (y + 1) / 2; // Invert Y-axis
      setCoords({ x: normalizedX, y: normalizedY });
      setAttributes(data.attributes);
    } catch (error) {
      console.error('Error fetching coordinates:', error);
      setError('Failed to fetch coordinates');
    }
  }, [word, provider]);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Left side - placeholder for future content */}
      <div className="flex-grow bg-gray-100">
        {/* Content for the left side will go here */}
      </div>

      {/* Resizer */}
      <div
        className="w-1 bg-gray-300 cursor-col-resize"
        onMouseDown={startResize}
      />

      {/* Right side - Control Panel */}
      <div
        className="bg-white shadow-lg overflow-y-auto"
        style={{ width: `${panelWidth}px` }}
      >
        <div className="p-5">
          <h2 className="text-2xl font-bold mb-4">Control Panel</h2>
          
          <div className="mb-4">
            <div 
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-4"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
            >
              <Upload className="mx-auto text-cyan-500 mb-4" size={48} />
              <p className="mb-2">Drag files to upload</p>
              <p className="text-sm text-gray-500 mb-4">or</p>
              <input
                type="file"
                accept=".json"
                onChange={(e) => onDrop(e.target.files)}
                className="hidden"
                id="fileInput"
              />
              <label htmlFor="fileInput" className="bg-cyan-500 text-white px-4 py-2 rounded-full cursor-pointer">
                Browse Files
              </label>
            </div>
            
            <p className="text-sm text-gray-500 mt-4">
              Max file size: 50MB
            </p>
            <p className="text-sm text-gray-500">
              Supported file type: JSON
            </p>
            
            {uploadStatus && (
              <div className="mt-6">
                <div className="bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className={`py-2 px-4 ${
                      uploadStatus.status === 'completed' ? 'bg-blue-500' : 
                      uploadStatus.status === 'error' ? 'bg-red-500' : 'bg-cyan-500'
                    }`}
                    style={{ width: `${uploadStatus.progress}%` }}
                  >
                    <div className="flex justify-between text-white">
                      <span>{uploadStatus.name}</span>
                      <span>{uploadStatus.size} bytes</span>
                    </div>
                  </div>
                  {uploadStatus.status === 'error' && (
                    <div className="text-red-500 flex items-center mt-1">
                      <AlertCircle size={16} className="mr-2" />
                      <span>Upload failed</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {message && <p className="mt-4">{message}</p>}
          </div>

          <div className='mb-4'>
            <input
              type="text"
              value={word}
              onChange={(e) => setWord(e.target.value)}
              placeholder="Enter a word"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50 p-2"
            />
          </div>
          <div className='mb-4'>
            <button
              onClick={fetchCoordinates}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Get Coords
            </button>
          </div>
          <p className="mt-4">{coords.x}, {coords.y}</p>
        </div>
      </div>
    </div>
  );
};

export default XCompass;