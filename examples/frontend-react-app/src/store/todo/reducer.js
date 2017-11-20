import * as types from './actionTypes'


export const initState = {
  todos: []
};

export default (state = initState, action) => {
  switch(action.type) {
    case types.TODOS_SET:
      return {...state, todos: action.payload.results, todos_count: action.payload.count};
    case types.TODOS_EXCLUDE:
      return {...state, todos: state.todos.filter(t => t.id !== action.payload), todos_count: state.todos_count - 1};
    case types.TODOS_REPLACE:
      return {...state, todos: state.todos.map(d => d.id === action.payload.id ? action.payload : d)};
    case types.TODOS_APPEND:
      return {...state, todos: state.todos.concat(action.payload), todos_count: state.todos_count + 1};
    default:
      return state;
  }
}
