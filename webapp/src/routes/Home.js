import React, { Component } from 'react'
import logo from './logo.png'
import './Home.css'
import { connect } from 'react-redux'
import cognitoUtils from '../lib/cognitoUtils'
import request from 'request'
import appConfig from '../config/app-config.json'
import CreateInstance from './CreateInstance'
import GetKey from './GetKey'


const mapStateToProps = state => {
  return { session: state.session }
}

class Home extends Component {
  constructor (props) {
    super(props)
    this.state = { apiStatus: 'Not called' , isLoaded: false}
  }

  updateAWS = () => {
    this.setState({apiStatus: 'Not called' , isLoaded: false});
    this.checkAWS();
  }

 checkAWS(){
    // Call the API server GET /list endpoint with our JWT access token
    const options = {
      url: `${appConfig.apiUri}`,
      headers: {
        Authorization: `Bearer ${this.props.session.credentials.idToken}`
      }
    }
    this.setState({ apiStatus: 'Loading...' })
    request.get(options, (err, resp, body) => {
      let apiStatus, apiResponse, isLoaded
      if (err) {
        // is API server started and reachable?
        apiStatus = 'Unable to reach API'
        isLoaded = false
        console.error(apiStatus + ': ' + err)
      } else if (resp.statusCode !== 200) {
        // API returned an error
        apiStatus = 'Error response received'
        isLoaded = false
        apiResponse = body
      } else {
        apiStatus = 'Successful response received.'
        //console.log('API RESPONSE')
        //console.log(body)
        apiResponse = JSON.parse(body)
        isLoaded = true
      }
      this.setState({ apiStatus, apiResponse , isLoaded})
    })
 } 
  componentDidMount () {
    if (this.props.session.isLoggedIn) {
      this.checkAWS()
    }
  }


  render () {
    return (
      <div className="Home">
        <header className="Home-header">
          <img src={logo} className="Home-logo" alt="logo" />
          { this.props.session.isLoggedIn ? (
            <div>
              <p> Welcome to CPE 453 EC2 Manager</p>
              <div className="Home-details"><p>You are logged in as user {this.props.session.user.userName} ({this.props.session.user.email}).</p></div>
              
              <div>
                <div className="Home-details">Contacting AWS: {this.state.apiStatus}</div>
                <div className="Home-details-strong">Current EC2 Allocation</div> 
                    { this.state.isLoaded ? (
                     <div>
                     <div className="Home-details">  
                        {this.instance = this.state.apiResponse.result.map((instance, key) =>
                            <div id={key}>
                              <p className="Home-api-response">Instance Info</p>
                            <p>Instance ID: {this.state.apiResponse['result'][key]['InstanceId']}</p>
                            <p>State:{this.state.apiResponse['result'][key]['State']}</p>
                            <p>Public_DNS:{this.state.apiResponse['result'][key]['Public_DNS']}</p>
                            <p>Public_IP:{this.state.apiResponse['result'][key]['Public_IP']}</p>
                            </div>
                        )
                       }   
                       </div>
                       <div>
                       <button onClick= {this.updateAWS} >Query Instance Status</button>
                       <GetKey session={this.props.session} action='key'></GetKey>
                       <CreateInstance session={this.props.session} action='create'></CreateInstance>
                       <CreateInstance session={this.props.session} action='stop'></CreateInstance>
                       <CreateInstance session={this.props.session} action='start'></CreateInstance>
                       <CreateInstance session={this.props.session} action='terminate'></CreateInstance>

                       
                        </div>
                        </div>
                        ) : (
                            <div></div>
                        )
                        
                        
                        
                    }
                    
              </div>
              <a className="Home-link" href="/signout">Sign out</a>
            </div>
          ) : (
            <div>
              <p>You are not logged in.</p>
              <a className="Home-link" href={cognitoUtils.getCognitoSignInUri()}>Sign in</a>
            </div>
          )}
          <div className="Home-details">
            <hr></hr>
            <div className="Home-details-links">
            
              
            </div>
          </div>
        </header>
      </div>
    )
  }
}

export default connect(mapStateToProps)(Home)
