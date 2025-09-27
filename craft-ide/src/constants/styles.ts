// Shared styles constants to reduce duplication
export const COMPONENT_STYLES = {
  console: {
    container: {
      flex: 2,
      padding: '10px',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#f5f5f5',
      overflow: 'auto'
    } as React.CSSProperties,
    tabs: {
      display: 'flex',
      borderBottom: '1px solid #ccc',
      flexShrink: 0
    } as React.CSSProperties,
    tab: {
      padding: '5px 10px',
      cursor: 'pointer'
    } as React.CSSProperties,
    activeTab: {
      borderBottom: '2px solid blue',
      fontWeight: 'bold'
    } as React.CSSProperties,
    content: {
      flexGrow: 1,
      marginTop: '10px',
      padding: '5px',
      border: '1px solid #eee',
      backgroundColor: 'white',
      overflow: 'auto',
      whiteSpace: 'pre-wrap',
      wordBreak: 'break-all'
    } as React.CSSProperties,
    button: {
      margin: '2px',
      padding: '5px',
      cursor: 'pointer'
    } as React.CSSProperties,
    table: {
      width: '100%',
      borderCollapse: 'collapse',
      marginTop: '10px'
    } as React.CSSProperties,
    th: {
      border: '1px solid #ddd',
      padding: '8px',
      backgroundColor: '#f2f2f2',
      textAlign: 'left'
    } as React.CSSProperties,
    td: {
      border: '1px solid #ddd',
      padding: '8px'
    } as React.CSSProperties
  },
  chat: {
    container: {
      flex: 1,
      borderBottom: '1px solid #ccc',
      padding: '10px',
      overflow: 'auto',
      display: 'flex',
      flexDirection: 'column'
    } as React.CSSProperties,
    messages: {
      flexGrow: 1,
      marginBottom: '10px',
      border: '1px solid #eee',
      padding: '5px',
      backgroundColor: 'white'
    } as React.CSSProperties,
    inputContainer: {
      display: 'flex',
      gap: '5px'
    } as React.CSSProperties
  }
} as const;