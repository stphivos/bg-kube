import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { Nav, NavItem, Well, Button, Glyphicon } from 'react-bootstrap'
import { BaseComponent } from '../utils/components'
import { ProfileEditor } from '../components/user'
import { userActions } from '../store'
import './Session.css'


class Session extends BaseComponent {
  componentDidMount() {
    this.attemptSignin();
  }

  attemptSignin = async() => {
    try {
      await this.props.loadLocalStorage();

      this.props.onSignedIn();
    } catch (_) {
      // No token in local storage
    }
  }

  onSignout = async(evt) => {
    try {
      evt.preventDefault();

      await this.props.signout();

      this.props.onSignedOut();
    } catch (err) {
      alert(err);
    }
  }

  onUpdateProfile = async(profile) => {
    await this.props.updateProfile(profile);
  }

  onAuthNavigate = (path) => {
    this.redirect(path);
  }

  render() {
    const { profile } = this.props.user;

    const content = profile ? (
        <Well bsSize="small" className="Session-Box">
          User: <label className="Session-Box-Username">{profile.username}</label>

          <div className="Session-Box-Actions">
            <ProfileEditor profile={profile} onSave={this.onUpdateProfile} className="Session-Box-Settings" bsStyle="primary" glyph="cog" label="Settings" />
            <Button onClick={this.onSignout} className="Session-Box-Signout"><Glyphicon glyph="log-out" /> Sign-out</Button>
          </div>
        </Well>
      ) : (
        <Nav bsStyle="pills" activeKey="/signin" className="Auth-Box" onSelect={this.onAuthNavigate}>
          <NavItem eventKey="/signup" className="Auth-Box-Signup">Sign-up</NavItem>
          <NavItem eventKey="/signin" className="Auth-Box-Signin">Sign-in</NavItem>
        </Nav>
      )

    return (
      <div className={this.props.className}>
        {content}
      </div>
    )
  }
}

const { loadLocalStorage, updateProfile, signout } = userActions;
export default connect(
  (state, ownProps) => ({user: state.user, onSignedIn: ownProps.onSignedIn, onSignedOut: ownProps.onSignedOut}),
  {loadLocalStorage, updateProfile, signout}
)(withRouter(Session));
