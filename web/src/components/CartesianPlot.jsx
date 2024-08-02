import React from 'react';

const CartesianPlot = ({ coords, attributes }) => {
  const data = { x: coords.x, y: coords.y };
  const axisLabel = "absolute flex items-center justify-center text-sm text-gray-600";
  const axisLine = "absolute bg-gray-300";


  const rangeValue = 5;
  const scaleCoordinate = (value, rangeValue) => ((value + rangeValue) / (2 * rangeValue)) * 100;




  return (
    <div className="mt-4 aspect-square bg-white p-4 relative flex items-center justify-center" style={{ height: '100vh' }}>
      <div className="w-3/4 h-3/4 bg-white shadow-md relative">
        {/* Horizontal axis line */}
        <div className={`${axisLine} left-0 top-1/2 w-full h-px`} />
        {/* Vertical axis line */}
        <div className={`${axisLine} top-0 left-1/2 h-full w-px`} />
        {/* Axis labels */}
        <div className={`${axisLabel} top-0 left-1/2 -translate-x-1/2`}>{attributes.positive_y}</div>
        <div className={`${axisLabel} bottom-0 left-1/2 -translate-x-1/2`}>{attributes.negative_y}</div>
        <div className={`${axisLabel} left-0 top-1/2 -translate-y-1/2`}>{attributes.negative_x}</div>
        <div className={`${axisLabel} right-0 top-1/2 -translate-y-1/2`}>{attributes.positive_x}</div>
        {/* Point and coordinate label */}
        <div className="absolute" style={{
          left: `${scaleCoordinate(data.x, rangeValue)}%`,
          top: `${100 - scaleCoordinate(data.y, rangeValue)}%`,
          transform: 'translate(-50%, -50%)'
        }}>
          <div className="w-2 h-2 bg-[#1DA1F2] rounded-full" />
          <div className="absolute top-0 left-10 transform -translate-y-full -translate-x-1/2 bg-gray-800 text-white px-2 py-1 rounded text-xs whitespace-nowrap">
            ({data.x.toFixed(2)}, {data.y.toFixed(2)})
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartesianPlot;
