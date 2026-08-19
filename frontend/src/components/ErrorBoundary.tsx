import React from "react";

interface ErrorBoundaryState {
  error: Error | null;
}

export default class ErrorBoundary extends React.Component<React.PropsWithChildren, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  render() {
    if (this.state.error) {
      return (
        <div className="card" role="alert">
          <div className="card-body">
            <h2 className="card-title">Something went wrong</h2>
            <p className="muted">{this.state.error.message || "An unexpected error occurred."}</p>
            <button className="btn btn-primary" onClick={() => this.setState({ error: null })}>
              Try again
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}