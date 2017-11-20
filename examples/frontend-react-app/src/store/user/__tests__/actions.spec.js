import { Reducer, Thunk } from 'redux-testkit'
import { UserService } from '../../../services'
import { LocalStorageMock } from '../../../utils/tests'
import { UnauthorizedError } from '../../../utils/errors'
import * as mocks from '../../../__mocks__/user'
import {
  reset, setToken, setProfile, signin, signout, loadProfile, reloadProfile,
  createProfile, updateProfile, loadLocalStorage
} from '../actions'


describe('User', () => {

  describe('Thunks', () => {
    const spies = [];

    beforeAll(() => {
      global.localStorage = new LocalStorageMock();
    })

    afterEach(() => {
      localStorage.clear();
      spies.forEach(s => s.mockRestore());
      spies.length = 0;
    })

    describe('signin', () => {
      it('Authenticates with service, sets token and loads profile', async() => {
        const token = mocks.getToken();
        spies.push(jest
          .spyOn(UserService.prototype, 'authenticate')
          .mockReturnValueOnce(token));

        const creds = ['username', 'password'];
        const state = mocks.getAnonymousState();

        const dispatches = await Thunk(signin).withState(state).execute(...creds);
        expect(dispatches.length).toBe(2);
        expect(dispatches[0].getAction()).toEqual(setToken(token));
        expect(dispatches[1].isFunction()).toBe(true);
        expect(dispatches[1].getName()).toBe('loadProfile');

        expect(spies[0]).toHaveBeenCalledWith(...creds);
      })
    })

    describe('signout', () => {
      it('Clears local storage and profile state', async() => {
        localStorage.setItem('token', JSON.stringify({any: 'token'}));
        localStorage.setItem('other', JSON.stringify({other: 'data'}));

        const dispatches = await Thunk(signout).execute();
        expect(localStorage.getItem('token')).toBe(null);
        expect(localStorage.getItem('other')).toBe(null);

        expect(dispatches.length).toBe(1);
        expect(dispatches[0].getAction()).toEqual(reset());
      })
    })

    describe('loadProfile', () => {
      it('Gets profile and dispatches setProfile', async() => {
        const profileAction = setProfile({id: 1});
        spies.push(jest
          .spyOn(UserService.prototype, 'getProfile')
          .mockReturnValueOnce(profileAction.payload));

        const state = mocks.getAnonymousState();
        const dispatches = await Thunk(loadProfile).withState(state).execute();

        expect(dispatches.length).toBe(1);
        expect(dispatches[0].getAction()).toEqual(profileAction);
      })

      it('Refreshes token and reloads profile when status 401', async() => {
        spies.push(jest
          .spyOn(UserService.prototype, 'getProfile')
          .mockImplementationOnce(() => {throw new UnauthorizedError()}));

        const tokenAction = setToken({any: 'token'});
        spies.push(jest
          .spyOn(UserService.prototype, 'refresh')
          .mockReturnValueOnce(tokenAction.payload));

        const state = mocks.getAnonymousState();
        const dispatches = await Thunk(loadProfile).withState(state).execute();
        expect(dispatches.length).toBe(2);
        expect(dispatches[0].getAction()).toEqual(tokenAction);
        expect(dispatches[1].isFunction()).toBe(true);
        expect(dispatches[1].getName()).toBe('reloadProfile');
      })
    })

    describe('reloadProfile', () => {
      it('Dispatches to loadProfile', async() => {
        const dispatches = await Thunk(reloadProfile).execute();
        expect(dispatches.length).toBe(1);
        expect(dispatches[0].isFunction()).toBe(true);
        expect(dispatches[0].getName()).toBe('loadProfile');
      })
    })

    describe('createProfile', () => {
      it('Registers profile and signs in anonymous user', async() => {
        spies.push(jest
          .spyOn(UserService.prototype, 'createProfile')
          .mockReturnValueOnce({}));

        const profile = mocks.getProfile();
        const state = mocks.getAnonymousState();

        const dispatches = await Thunk(createProfile).withState(state).execute(profile);
        expect(dispatches.length).toBe(1);
        expect(dispatches[0].isFunction()).toBe(true);
        expect(dispatches[0].getName()).toBe('signin');

        expect(spies[0]).toHaveBeenCalledWith(profile);
      })
    })

    describe('updateProfile', () => {
      it('Patches a profile and sets updated profile as current', async() => {
        const updatedProfile = mocks.getProfile();
        spies.push(jest
          .spyOn(UserService.prototype, 'patchProfile')
          .mockReturnValueOnce(updatedProfile));

        const profile = mocks.getProfile();
        const state = mocks.getLoggedInState();

        const dispatches = await Thunk(updateProfile).withState(state).execute(profile);
        expect(dispatches.length).toBe(1);
        expect(dispatches[0].getAction()).toEqual(setProfile(updatedProfile));

        expect(spies[0]).toHaveBeenCalledWith(profile);
      })
    })

    describe('loadLocalStorage', () => {
      it('Throws an error if a token is not found', () => {
        expect(() => { Thunk(loadLocalStorage).execute() }).toThrow();
      })

      it('Sets token and loads profile if a token is found', async() => {
        const token = {any: 'token'};
        localStorage.setItem('token', JSON.stringify(token));

        const dispatches = await Thunk(loadLocalStorage).execute();
        expect(dispatches.length).toBe(2);
        expect(dispatches[0].getAction()).toEqual(setToken(token));
        expect(dispatches[1].isFunction()).toBe(true);
        expect(dispatches[1].getName()).toBe('loadProfile');
      })
    })
  })
})
