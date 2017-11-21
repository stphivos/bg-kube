import { Reducer, Thunk } from 'redux-testkit'
import { reducer, initState, types } from '..'
import { LocalStorageMock } from '../../../utils/tests'
import { UnauthorizedError } from '../../../utils/errors'
import * as mocks from '../../../__mocks__/user'


describe('User', () => {

  describe('Reducer', () => {
    it('Returns initial state', () => {
      expect(reducer(undefined, {type: 'ANYTHING'})).toEqual(initState);
    })

    it('Returns a new state with the token', () => {
      const token = {access_token: 'access', refresh_token: 'refresh'};
      const action = {type: types.SET_TOKEN, payload: token};
      Reducer(reducer).expect(action)
        .toReturnState({...initState, token});
    })

    it('Returns a new state with the profile', () => {
      const profile = {id: 1, username: 'admin'};
      const action = {type: types.SET_PROFILE, payload: profile};
      Reducer(reducer).expect(action)
        .toReturnState({...initState, profile});
    })
  })
})
