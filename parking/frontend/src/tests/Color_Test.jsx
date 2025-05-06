import React, { useState } from 'react'

const Color_Test = () => {
  const [color, setColor] = useState('#3498db');

  const handleColorChange = (e) => setColor(e.target.value);

  return (
    <>
      <div>
        style needs an object as input 
        <h1 style={{ color: color }}>Dynamic Color</h1>
        <input type="color" value={color} onChange={handleColorChange} />
      </div>
    </>
  )
}

export default Color_Test

