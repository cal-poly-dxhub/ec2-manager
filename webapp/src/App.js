import React from 'react'
import {
  Router,
  Route
} from 'react-router-dom'
import Callback from './routes/Callback'
import Home from './routes/Home'
import Signout from './routes/Signout'

import { createBrowserHistory } from 'history'

const history = createBrowserHistory()

const App = () => (
  <Router history={history}>
    <Route exact path="/" component={Home}/>
    <Route exact path="/signout" component={Signout}/>
    <Route exact path="/callback" component={Callback}/>
  </Router>
)

export default App
