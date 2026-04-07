import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  componentDidCatch(error) {
    console.error('WebApp fatal render error:', error);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 16, color: '#fff' }}>
          <h3>App-Fehler</h3>
          <p>Bitte Mini App neu oeffnen.</p>
        </div>
      );
    }
    return this.props.children;
  }
}
