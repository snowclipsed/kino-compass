import React, { useCallback, useState, useRef } from 'react';
import axios from 'axios';
import { Upload, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import CartesianPlot from './CartesianPlot';

const XCompass = ({ provider }) => {
  const [fileMessage, setFileMessage] = useState({ text: '', type: '' });
  const [word, setWord] = useState('');
  const [wordMessage, setWordMessage] = useState('');
  const [coords, setCoords] = useState({ x: 0.0, y: 0.0 });
  const [error, setError] = useState('');
  const [uploadStatus, setUploadStatus] = useState(null);
  const [panelWidth, setPanelWidth] = useState(400);
  const [isLoading, setIsLoading] = useState(false);
  const resizeRef = useRef(null);

  const [attributes, setAttributes] = useState({
    x_positive: '',
    x_negative: '',
    x_aspect: '',
    y_positive: '',
    y_negative: '',
    y_aspect: ''
  });


const handleMouseMove = useCallback((e) => {
    if (resizeRef.current) {
      const newWidth = window.innerWidth - e.clientX;
      setPanelWidth(Math.max(300, Math.min(newWidth, window.innerWidth - 300)));
    }
  }, []);

  const handleMouseUp = useCallback(() => {
    resizeRef.current = null;
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  }, [handleMouseMove]);

  const startResize = (e) => {
    e.preventDefault();
    resizeRef.current = true;
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };


  const onDrop = useCallback((acceptedFiles) => {
    const selectedFile = acceptedFiles[0];
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
      setFileMessage({text: 'Please select a file first.', type: 'error'});
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
      setFileMessage({text: response.data.message, type:response.data.status});
      setUploadStatus(prev => ({ ...prev, status: 'completed' }));
    } catch (error) {
      console.error("Error uploading file:", error.message);
      setUploadStatus(prev => ({ ...prev, status: 'error' }));
    }
  };

  const fetchCoordinates = useCallback(async () => {
    if (!word) {
      setWordMessage('Please enter a word');
      return;
    }
    setError(null);
    setFileMessage({ text: '', type: '' });
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/get-coords', {
        word,
        provider,
      });

      const data = response.data;
      const [x, y] = data.coordinates;
      const normalizedX = (x + 1) / 2;
      const normalizedY = 1 - (y + 1) / 2; // Invert Y-axis
      setCoords({ x: normalizedX, y: normalizedY });
      setAttributes(data.attributes);
    } catch (error) {
      if (error.response) {
        const errorData = error.response.data;
        if (error.response.status === 400) {
          setFileMessage({ text: errorData.error, type: 'error' });
        } else {
          console.error('Failed to fetch coordinates:', error);
          setError('Failed to fetch coordinates');
        }
      } else {
        console.error('Error fetching coordinates:', error);
        setError('Failed to fetch coordinates');
      }
    } finally {
      setIsLoading(false);
    }
  }, [word, provider]);


  const handleReload = () => {
    window.location.reload();
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Left side - Cartesian Plot */}
      <div className="flex-grow bg-white p-4 relative flex items-center justify-center">
        <CartesianPlot coords={coords} attributes={attributes}/>
      </div>

      {/* Resizer */}
      <div
        className="w-1 bg-gray-200 cursor-col-resize"
        onMouseDown={(e) => startResize(e)}
        style={{ width: '5px', cursor: 'col-resize'}}
      />

      {/* Right side - Control Panel */}
      <div
        className="bg-white shadow-lg overflow-y-auto"
        style={{ width: `${panelWidth}px` }}
      >
        <div className="p-5">
          <h2 className="text-2xl font-bold mb-4 text-center cursor-pointer" onClick={handleReload}>𝕏 Compass</h2> 
          <div className="mb-4">
            <div 
              className="border-2 border-dashed border-gray-400 rounded-lg p-8 text-center mb-4"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
            >
              <Upload className="mx-auto text-black mb-4" size={48} />
              <p className="mb-2">Drag files to upload</p>
              <p className="text-sm text-black mb-4">or</p>
              <input
                type="file"
                accept=".json"
                onChange={(e) => onDrop(e.target.files)}
                className="hidden"
                id="fileInput"
              />
              <label htmlFor="fileInput" className="bg-[#1DA1F2] text-white px-4 py-2 rounded-full cursor-pointer hover:bg-[#1a91da]">               
                Browse Files
              </label>
            </div>
            
            <p className="text-sm text-gray-500 mt-4">
            </p>
            <p className="text-sm text-gray-500">
              Supported file type: JSON
            </p>
            
            {uploadStatus && (
              <div className="mt-6">
                <div className="bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className={`py-2 px-4 ${
                      uploadStatus.status === 'completed' ? 'bg-[#1DA1F2]' : 
                      uploadStatus.status === 'error' ? 'bg-red-500' : 'bg-cyan-500'
                    }`}
                    style={{ width: `${uploadStatus.progress}%` }}
                  >
                    <div className="flex justify-between text-white">
                      <span>{uploadStatus.name}</span>
                      <span>{(uploadStatus.size/1048576).toFixed(2)} MB</span>
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

            {fileMessage.text && (
            <div className={`mt-4 flex items-center ${
              fileMessage.type === 'success' ? 'text-green-500' : 'text-red-500'
            }`}>
              {fileMessage.type === 'success' ? (
                <CheckCircle size={16} className="mr-2" />
              ) : (
                <AlertCircle size={16} className="mr-2" />
              )}
              <p>{fileMessage.text}</p>
            </div>
          )}
          </div>

          <div className='mb-4'>
            <input
              type="text"
              value={word}
              onChange={(e) => setWord(e.target.value)}
              placeholder="Enter a word"
              className="mt-1 block w-full rounded-md border-gray-500 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50 p-2"
            />
            {wordMessage && <p className="text-red-500 mt-1">{wordMessage}</p>}
          </div>
          <div className='mb-4 relative flex items-center justify-center'>
            <button
              onClick={fetchCoordinates}
              className="bg-[#1DA1F2] text-white px-4 py-2 rounded-full hover:bg-[#1a91da]"
              disabled={isLoading}
            >
              Get Results!
            </button>
          </div>
              {isLoading && (
                <div className="flex justify-center items-center mt-4">
                  <Loader className="animate-spin text-blue-500" size={24} />
                  <span className="ml-2 text-blue-500">Loading...</span>
                </div>
              )}
            {error && <p className="text-red-500 mt-4">{error}</p>}
        </div>
      </div>
    </div>
  );
};

export default XCompass;
