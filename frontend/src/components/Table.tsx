import React from 'react'

export function Table({ children }: { children: React.ReactNode }) {
  return <div style={{ overflowX: 'auto' }}><table className="table">{children}</table></div>
}

