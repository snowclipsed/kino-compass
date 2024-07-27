import React, { useState, useEffect } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip, ResponsiveContainer } from 'recharts';

const XCompass = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    // Fetch data from backend
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/get-twitter-data');
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error('Error fetching Twitter data:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="w-full h-screen flex flex-col items-center justify-center bg-gray-900 text-white p-4">
      <h1 className="text-4xl font-bold mb-8">Twitter Compass</h1>
      <div className="w-full h-3/4">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <XAxis type="number" dataKey="x" name="X Axis" unit="" />
            <YAxis type="number" dataKey="y" name="Y Axis" unit="" />
            <ZAxis type="number" dataKey="z" range={[64, 144]} name="score" unit="km" />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            <Scatter name="X Data" data={data} fill="#8884d8" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default XCompass;
