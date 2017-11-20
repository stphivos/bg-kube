import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { Button, FormControl } from 'react-bootstrap'
import { ModelComponent } from '../utils/components'
import { userActions } from '../store'


class SigninForm extends ModelComponent {
  state = {
    username: '',
    password: ''
  }

  handleSubmit = async(evt) => {
    try {
      evt.preventDefault();

      const { username, password } = this.state;
      await this.props.signin(username, password);

      this.props.onSignedIn();
    } catch (err) {
      this.setError(err);
    }
  }

  render() {
    return (
      <div className="Signin-Page">
        <h3>Sign in</h3>

        {this.messageAlert()}

        <form onSubmit={this.handleSubmit}>
          {this.field('username', <FormControl type="text" />)}
          {this.field('password', <FormControl type="password" />)}

          <Button bsStyle="primary" type="submit">Submit</Button>
          <Button onClick={this.props.history.goBack}>Back</Button>
        </form>
      </div>
    );
  }
}

const { signin } = userActions;
export default connect(
  (state, ownProps) => ({onSignedIn: ownProps.onSignedIn}),
  {signin}
)(withRouter(SigninForm));
