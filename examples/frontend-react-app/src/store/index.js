import {createStore, applyMiddleware, combineReducers} from 'redux'
import {composeWithDevTools} from 'redux-devtools-extension'
import thunk from 'redux-thunk'
import {reducer as userReducer, types as userTypes} from './user'
import {reducer as todoReducer} from './todo'


const appReducer = combineReducers({
  user: userReducer,
  todo: todoReducer
});

const reducer = (state, action) => {
  if (action.type === userTypes.RESET) {
    state = undefined;
  }

  return appReducer(state, action);
};

export default createStore(
  reducer,
  composeWithDevTools(
    applyMiddleware(thunk)
  )
);

export {actions as userActions} from './user'
export {actions as todoActions} from './todo'
