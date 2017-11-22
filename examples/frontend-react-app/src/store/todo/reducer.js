import * as types from './actionTypes'


export const initState = {
  todos: []
};

export default (state = initState, action) => {
  switch(action.type) {
    case types.TODOS_SET:
      return {...state, todos: ordered(action.payload.results), todos_count: action.payload.count};
    case types.TODOS_EXCLUDE:
      return {...state, todos: ordered(state.todos.filter(t => t.id !== action.payload)), todos_count: state.todos_count - 1};
    case types.TODOS_REPLACE:
      return {...state, todos: ordered(state.todos.map(d => d.id === action.payload.id ? action.payload : d))};
    case types.TODOS_APPEND:
      return {...state, todos: ordered(state.todos.concat(action.payload)), todos_count: state.todos_count + 1};
    default:
      return state;
  }
}

export const ordered = (todos) => todos.sort((a, b) => a.priority - b.priority);
