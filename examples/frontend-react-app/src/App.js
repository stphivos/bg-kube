import React, { Component } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom'
import { Link } from 'react-router-dom'
import { Jumbotron } from 'react-bootstrap'
import { PublicRoute, PrivateRoute } from './utils/routes'
import { Session, Home, Signin, Signup, Todos } from './containers'
import logo from './logo.svg';
import './App.css';

class App extends Component {
  state = {
    auth: false
  }

  onSignedIn = () => {
    this.setState({ auth: true });
  }

  onSignedOut = () => {
    this.setState({ auth: false });
  }

  render() {
    return (
      <Router>
        <div className="App">
          <Jumbotron className="App-header">
            <Link to="/">
              <img src={logo} className="App-logo" alt="logo" />
            </Link>
            <h2>Todo's</h2>
            ({process.env.NODE_ENV}{process.env.REACT_APP_COLOR ? `-${process.env.REACT_APP_COLOR}` : ''})
          </Jumbotron>
          <Switch>
            <Route path="/:name?" render={({match}) => (
              ['/signin', '/signup'].includes(`/${match.params.name}`)
                ? null
                : <Session className="App-session centered-box" onSignedIn={this.onSignedIn} onSignedOut={this.onSignedOut} />
            )} />
          </Switch>
          <div className="App-body centered-box">
            <Switch>
              <PublicRoute exact path="/" auth={this.state.auth} component={Home} />
              <PublicRoute path="/signup" auth={this.state.auth} component={() => (<Signup onSignedIn={this.onSignedIn} />)} />
              <PublicRoute path="/signin" auth={this.state.auth} component={() => (<Signin onSignedIn={this.onSignedIn} />)} />
              <PrivateRoute path="/todos" auth={this.state.auth} component={Todos} />
            </Switch>
          </div>
        </div>
      </Router>
    );
  }
}

export default App;
