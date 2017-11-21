import fetchMock from 'jest-fetch-mock'
import UserService from '../user'
import * as mocks from '../../__mocks__/user'
import { UnauthorizedError } from '../../utils/errors'


global.fetch = fetchMock;

describe('User', () => {

  describe('Services', () => {

    describe('authenticate', () => {
      it('Calls auth-api and returns a token when status 200', async() => {
        const token = mocks.getToken();
        fetch.mockResponseOnce(JSON.stringify(token), { status: 200 });

        const service = new UserService(mocks.getAnonymousState());
        const result = await service.authenticate('username', 'password');

        expect(result).toEqual(token);
      })
    })

    describe('refresh', () => {
      it('Calls auth-api and returns a refresh token when status 200', async() => {
        const refresh_token = mocks.getToken();
        fetch.mockResponseOnce(JSON.stringify(refresh_token), { status: 200 });

        const service = new UserService(mocks.getLoggedInState());
        const result = await service.refresh();

        expect(result).toEqual(refresh_token);
      })
    })

    describe('getProfile', () => {
      it('Gets a profile from profile-api and returns the json result object', async() => {
        const profile = mocks.getProfile();
        fetch.mockResponseOnce(JSON.stringify(profile), { status: 200 });

        const service = new UserService(mocks.getLoggedInState());
        const result = await service.getProfile();

        expect(result).toEqual(profile);
      })

      it('Calls profile-api and throws unauthorized error when status 401', async() => {
        fetch.mockResponseOnce(JSON.stringify({not: 'a profile'}), { status: 401 });

        const service = new UserService(mocks.getLoggedInState());
        let error;

        try {
          await service.getProfile();
        } catch (e) {
          error = e;
        }

        expect(error).toBeInstanceOf(UnauthorizedError);
      })
    })

    describe('createProfile', () => {
      it('Posts a profile to profile-api and returns the json result object', async() => {
        const profile = mocks.getProfile();
        fetch.mockResponseOnce(JSON.stringify(profile), { status: 201 });

        const service = new UserService(mocks.getAnonymousState());
        const result = await service.createProfile(profile);

        expect(result).toEqual(profile);
      })
    })

    describe('patchProfile', () => {
      it('Calls profile-api to patch fields sent and returns the json result object', async() => {
        const updatedProfile = mocks.getProfile();
        fetch.mockResponseOnce(JSON.stringify(updatedProfile), { status: 200 });

        const service = new UserService(mocks.getLoggedInState());
        const result = await service.patchProfile(mocks.getProfile());

        expect(result).toEqual(updatedProfile);
      })
    })
  })
})
