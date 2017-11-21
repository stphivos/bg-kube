import * as types from './actionTypes'
import { UserService } from '../../services'
import { UnauthorizedError } from '../../utils/errors'


export const reset = () => ({type: types.RESET});
export const setToken = (token) => ({type: types.SET_TOKEN, payload: token});
export const setProfile = (profile) => ({type: types.SET_PROFILE, payload: profile});

export const getService = (getState) => {
  return new UserService(getState());
}

export const storeToken = (dispatch, token) => {
  localStorage.setItem('token', JSON.stringify(token));
  dispatch(setToken(token));
}

export const signin = (username, password) => {
  return async function signin(dispatch, getState) {
    const service = getService(getState);

    const token = await service.authenticate(username, password);
    storeToken(dispatch, token);

    return dispatch(loadProfile());
  }
}

export const signout = () => {
  return (dispatch) => {
    localStorage.clear();

    return dispatch(reset());
  }
}

export const loadProfile = () => {
  return async function loadProfile(dispatch, getState) {
    const service = getService(getState);

    try {
      const profile = await service.getProfile();
      dispatch(setProfile(profile));
    } catch (err) {
      if (err instanceof UnauthorizedError) {
        const token = await service.refresh();
        storeToken(dispatch, token);

        return dispatch(reloadProfile());
      } else {
        dispatch(signout());

        throw err;
      }
    }
  }
}

export const reloadProfile = () => {
  return async function reloadProfile(dispatch) {
    return dispatch(loadProfile());
  }
}

export const createProfile = (profile) => {
  return async function createProfile(dispatch, getState) {
    const service = getService(getState);
    await service.createProfile(profile);

    return dispatch(signin(profile.username, profile.password));
  }
}

export const updateProfile = (profile) => {
  return async function updateProfile(dispatch, getState) {
    const service = getService(getState);
    const updatedProfile = await service.patchProfile(profile);

    return dispatch(setProfile(updatedProfile));
  }
}

export const loadLocalStorage = () => {
  return (dispatch) => {
    const data = localStorage.getItem('token');
    if (data) {
      const token = JSON.parse(data);
      dispatch(setToken(token));

      return dispatch(loadProfile());
    } else {
      throw new Error('No token found');
    }
  }
}
