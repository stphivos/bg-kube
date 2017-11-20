import React from 'react'
import { Route } from 'react-router-dom'
import { Redirect } from 'react-router'


export const PrivateRoute = ({component: Component, auth, render, computedMatch, ...otherProps}) => {
  return (
    <Route
      {...JSON.stringify(otherProps)}
      render={(props) => auth === true
        ? render ? render({match: computedMatch}) : <Component {...props} />
        : <Redirect to={{pathname: '/', state: {from: props.location}}} />}
    />
  )
}

export const PublicRoute = ({component: Component, auth, render, computedMatch, ...otherProps}) => {
  return (
    <Route
      {...otherProps}
      render={(props) => auth === true
        ? <Redirect to={otherProps.location.state ? otherProps.location.state.from.pathname : '/todos'} />
        : render ? render({match: computedMatch}) : <Component {...props} />}
    />
  )
}
