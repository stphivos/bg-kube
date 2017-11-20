export class Service {
  constructor(state) {
    this.token = state.user.token;

    this.client_id = process.env.REACT_APP_CLIENT_ID;
    this.client_secret = process.env.REACT_APP_CLIENT_SECRET;

    this.userApi = process.env.REACT_APP_USER_API;
    this.todoApi = process.env.REACT_APP_TODO_API;

    this.payload = {
      headers: {
        'Content-Type': 'application/json'
      }
    };
  }

  api(name) {
    switch (name) {
      case 'user':
        this.payload.host = this.userApi;
        break;
      case 'todo':
        this.payload.host = this.todoApi;
        break;
      default:
        break;
    }

    return this;
  }

  request(method, url) {
    this.payload.method = method;
    this.payload.url = url;

    return this;
  }

  get(url) {
    return this.request('GET', url);
  }

  post(url) {
    return this.request('POST', url);
  }

  patch(url) {
    return this.request('PATCH', url);
  }

  put(url) {
    return this.request('PUT', url);
  }

  delete(url) {
    return this.request('DELETE', url);
  }

  body(obj) {
    this.payload.body = obj;

    return this;
  }

  auth(type) {
    switch (type) {
      case 'basic':
        this.payload.headers['Authorization'] = 'Basic ' + btoa(`${this.client_id}:${this.client_secret}`)
        break;
      case 'bearer':
        this.payload.headers['Authorization'] = `Bearer ${this.token.access_token}`;
        break;
      default:
        break;
    }

    return this;
  }

  contentType(type) {
    this.payload.headers['Content-Type'] = type;

    return this;
  }

  urlEncodeObj = (...objects) => {
    const obj = Object.assign({}, ...objects)
    const str = [];
    for (const p in obj)
      if (obj.hasOwnProperty(p) && obj[p]) {
        str.push(encodeURIComponent(p) + '=' + encodeURIComponent(obj[p]));
      }
    return str.join('&');
  }

  getUrl(params) {
    const query = this.urlEncodeObj(params || {});

    return `${this.payload.host}${this.payload.url}?${query}`;
  }

  getBody() {
    switch (this.payload.headers['Content-Type']) {
      case 'application/x-www-form-urlencoded':
        return this.urlEncodeObj(this.payload.body);
      default:
        return JSON.stringify(this.payload.body);
    }
  }

  getHeaders() {
    const obj = {};
    for (const key in this.payload.headers) {
      obj[key] = this.payload.headers[key];
    }
    return obj;
  }

  then(callback) {
    return fetch(this.getUrl(), {
      method: this.payload.method,
      headers: this.getHeaders(),
      body: this.getBody()
    })
    .then(callback);
  }

  json_if = (response, status) => {
    return new Promise((resolve, reject) => {
      response
        .json()
        .then(obj => {
          if (response.status === status) {
            resolve(obj);
          } else {
            reject(obj.error_description || obj.non_field_errors || response.statusText);
          }
        })
        .catch(err => {
          reject(response.statusText);
        })
    })
  }

  throw_if_not = (response, status) => {
    if (response.status !== status) {
      throw new Error(response.statusText);
    }
  }
}
