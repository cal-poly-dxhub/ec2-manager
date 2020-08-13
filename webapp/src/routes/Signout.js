import React, { Component } from 'react'
import logo from './logo.png'
import './Signout.css'
import { connect } from 'react-redux'
import cognitoUtils from '../lib/cognitoUtils'

const mapStateToProps = state => {
  return { session: state.session }
}

class Signout extends Component {
  constructor (props) {
    super(props)
    this.state = { apiStatus: 'Not called' }
  }

  componentDidMount () {
    if (this.props.session.isLoggedIn) {
      this.onSignOut()
    }
  }

  onSignOut = (e) => {
    e.preventDefault()
    cognitoUtils.signOutCognitoSession()
  }

  render () {
    return (
      <div className="Signout">
        <header className="Signout-header">
          <img src={logo} className="Signout-logo" alt="logo" />
          { this.props.session.isLoggedIn ? (
            <div>
              <h3> Welcome to ec2 Manager</h3>
              <p>You are logged in as user {this.props.session.user.userName} ({this.props.session.user.email}).</p>
              <p></p>
              <a className="Signout-link" href="/signout" onClick={this.onSignOut}>Sign out</a>
            </div>
          ) : (
            <div>
              <p>You are not logged in.</p>
              <a className="Signout-link" href={cognitoUtils.getCognitoSignInUri()}>Sign in</a>
            </div>
          )}
        </header>
      </div>
    )
  }
}

export default connect(mapStateToProps)(Signout)
