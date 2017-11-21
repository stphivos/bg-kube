import { Service } from '../utils/services'
import { UnauthorizedError } from '../utils/errors'


class UserService extends Service {
  authenticate(username: string, password: string) {
    return this
      .api('user')
      .post('/oauth2/token/')
      .body({grant_type: 'password', username, password})
      .auth('basic')
      .contentType('application/x-www-form-urlencoded')
      .then(res => this.json_if(res, 200))
  }

  refresh() {
    const { client_id, client_secret, token: { refresh_token } } = this;
    return this
      .api('user')
      .post('/oauth2/token/')
      .body({grant_type: 'refresh_token', client_id, client_secret, refresh_token})
      .contentType('application/x-www-form-urlencoded')
      .then(res => this.json_if(res, 200))
  }

  getProfile() {
    return this
      .api('user')
      .get('/user/')
      .auth('bearer')
      .then(res => {
        if (res.status === 401) {
          throw new UnauthorizedError();
        } else {
          return this.json_if(res, 200);
        }
      })
  }

  createProfile(profile) {
    return this
      .api('user')
      .post('/user/')
      .body(profile)
      .then(res => this.json_if(res, 201))
  }

  patchProfile(profile) {
    return this
      .api('user')
      .patch('/user/')
      .body(profile)
      .auth('bearer')
      .then(res => this.json_if(res, 200))
  }
}

export default UserService;
