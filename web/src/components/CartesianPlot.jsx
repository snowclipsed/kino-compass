import React from 'react';

const CartesianPlot = ({ coords, attributes }) => {
  const data = { x: coords.x, y: coords.y };

  const axisLabel = "absolute flex items-center justify-center text-sm text-gray-600";
  const axisLine = "absolute bg-gray-300";

  return (
    <div className="mt-4 w-full aspect-square bg-gray-100 p-4 relative">
        <div className="w-full h-full bg-white shadow-md relative">
        {/* Horizontal axis line */}
        <div className={`${axisLine} left-0 top-1/2 w-full h-px`} />
        {/* Vertical axis line */}
        <div className={`${axisLine} top-0 left-1/2 h-full w-px`} />

        {/* Axis labels */}
        <div className={`${axisLabel} top-0 left-1/2 -translate-x-1/2`}>{attributes.positive_y}</div>
        <div className={`${axisLabel} bottom-0 left-1/2 -translate-x-1/2`}>{attributes.negative_y}</div>
        <div className={`${axisLabel} left-0 top-1/2 -translate-y-1/2`}>{attributes.negative_x}</div>
        <div className={`${axisLabel} right-0 top-1/2 -translate-y-1/2`}>{attributes.positive_x}</div>

        <div
        className="absolute w-2 h-2 bg-blue-500 rounded-full transform -translate-x-1 -translate-y-1"
        style={{ left: `${data.x * 100}%`, top: `${data.y * 100}%` }}
        title={`X: ${data.x.toFixed(2)}, Y: ${data.y.toFixed(2)}`}
        />
        </div>
  </div>
  );
};


export default CartesianPlot;