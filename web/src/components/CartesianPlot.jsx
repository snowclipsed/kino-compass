import React, { useRef } from 'react';
import html2canvas from 'html2canvas';

const CartesianPlot = ({ coords, attributes }) => {
  const data = { x: coords.x, y: coords.y };
  const rangeValue = 5;
  const scaleCoordinate = (value, rangeValue) => ((value + rangeValue) / (2 * rangeValue)) * 100;
  const plotRef = useRef(null);

  const handleSaveImage = async () => {
    if (plotRef.current) {
      const canvas = await html2canvas(plotRef.current);
      const image = canvas.toDataURL("image/png");
      const link = document.createElement('a');
      link.href = image;
      link.download = 'your-compass.png';
      link.click();
    }
  };

  return (
    <div className="mt-4 flex flex-col items-center">
      <div ref={plotRef} className="aspect-square p-4 relative flex items-center justify-center" style={{ height: '80vh', width: '80vh' }}>
        <div className="w-full h-full relative">
          {/* Colored quadrants */}
          <div className="absolute top-0 left-0 w-1/2 h-1/2 bg-red-200" />
          <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-blue-200" />
          <div className="absolute bottom-0 left-0 w-1/2 h-1/2 bg-green-200" />
          <div className="absolute bottom-0 right-0 w-1/2 h-1/2 bg-yellow-200" />
          
          {/* SVG for axes, arrows, and labels */}
          <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            {/* Horizontal axis */}
            <line x1="0" y1="50" x2="100" y2="50" stroke="black" strokeWidth="0.5" />
            <polygon points="0,50 2,49 2,51" fill="black" />
            <polygon points="100,50 98,49 98,51" fill="black" />
            
            {/* Vertical axis */}
            <line x1="50" y1="100" x2="50" y2="0" stroke="black" strokeWidth="0.5" />
            <polygon points="50,0 49,2 51,2" fill="black" />
            <polygon points="50,100 49,98 51,98" fill="black" />
            
            {/* Axis labels */}
            <text x="98" y="53" textAnchor="end" fontSize="3">{attributes.x_positive}</text>
            <text x="3" y="53" textAnchor="start" fontSize="3">{attributes.x_negative}</text>
            <text x="51" y="3" textAnchor="start" fontSize="3">{attributes.y_positive}</text>
            <text x="51" y="98" textAnchor="start" fontSize="3">{attributes.y_negative}</text>
          </svg>
          
          {/* Point */}
          <div className="absolute" style={{
            left: `${scaleCoordinate(data.x, rangeValue)}%`,
            top: `${100 - scaleCoordinate(data.y, rangeValue)}%`,
            transform: 'translate(-50%, -50%)'
          }}>
            <div className="w-2 h-2 bg-[#1DA1F2] rounded-full" />
          </div>
        </div>
      </div>
      <button
        onClick={handleSaveImage}
        className="mt-4 px-4 py-2 bg-[#1DA1F2] text-white rounded hover:bg-blue-600 transition-colors"
      >
        Save as Image
      </button>
    </div>
  );
};

export default CartesianPlot;