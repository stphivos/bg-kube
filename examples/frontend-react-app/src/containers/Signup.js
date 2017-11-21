import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { Button, FormControl } from 'react-bootstrap'
import { ModelComponent } from '../utils/components'
import { userActions } from '../store'


class SignupForm extends ModelComponent {
  state = {
    profile: {
      username: '',
      password: '',
      first_name: '',
      last_name: ''
    }
  }

  handleSubmit = async(evt) => {
    try {
      evt.preventDefault();

      const { profile } = this.state;
      await this.props.createProfile(profile);

      this.props.onSignedIn();
    } catch (err) {
      this.setError(err);
    }
  }

  render() {
    return (
      <div className="Signup-Page">
        <h3>Sign up</h3>

        {this.messageAlert()}

        <form onSubmit={this.handleSubmit}>
          {this.field('profile.username', <FormControl type="text" />)}
          {this.field('profile.password', <FormControl type="password" />)}
          {this.field('profile.first_name', <FormControl type="text" />)}
          {this.field('profile.last_name', <FormControl type="text" />)}

          <Button bsStyle="primary" type="submit">Submit</Button>
          <Button onClick={this.props.history.goBack}>Back</Button>
        </form>
      </div>
    );
  }
}

const { createProfile } = userActions;
export default connect(
  (state, ownProps) => ({onSignedIn: ownProps.onSignedIn}),
  {createProfile}
)(withRouter(SignupForm));
