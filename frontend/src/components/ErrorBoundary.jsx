import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ error, errorInfo });
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '40px', textAlign: 'center', background: '#ffebee', color: '#c62828', minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
          <h1 style={{ marginBottom: '16px' }}>Something went wrong.</h1>
          <p style={{ marginBottom: '24px' }}>The application encountered an unexpected error.</p>
          <details style={{ whiteSpace: 'pre-wrap', textAlign: 'left', background: '#fff', padding: '20px', borderRadius: '8px', border: '1px solid #ef9a9a', maxWidth: '800px', width: '100%' }}>
            {this.state.error && this.state.error.toString()}
            <br />
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </details>
          <button 
            onClick={() => window.location.reload()} 
            style={{ marginTop: '24px', padding: '10px 20px', background: '#c62828', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children; 
  }
}
