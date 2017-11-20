import Chance from 'chance'


const chance = new Chance();

export const getToken = () => {
  return {
    access_token: chance.string(),
    refresh_token: chance.string()
  }
}

export const getProfile = () => {
  return {
    id: chance.integer({min: 1}),
    username: chance.string(),
    first_name: chance.string(),
    last_name: chance.string()
  }
}

export const getAnonymousState = () => {
  return {
    user: {
      token: {},
      profile: {}
    }
  }
}

export const getLoggedInState = () => {
  return {
    user: {
      token: getToken(),
      profile: getProfile()
    }
  }
}
