import * as types from './actionTypes'


export const initState = {
  'token': null,
  'profile': null
};

export default (state = initState, action) => {
  switch(action.type) {
    case types.SET_TOKEN:
      return {...state, token: action.payload};
    case types.SET_PROFILE:
      return {...state, profile: action.payload};
    default:
      return state;
  }
}
