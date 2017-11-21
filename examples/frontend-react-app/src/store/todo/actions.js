import * as types from './actionTypes'
import { TodoService } from '../../services'


const setTodos = (todos) => ({type: types.TODOS_SET, payload: todos});
const excludeTodo = (id) => ({type: types.TODOS_EXCLUDE, payload: id});
const replaceTodo = (todo) => ({type: types.TODOS_REPLACE, payload: todo});
const appendTodo = (todo) => ({type: types.TODOS_APPEND, payload: todo});

export const getService = (getState) => {
  return new TodoService(getState());
}

export const loadTodos = () => {
  return async function loadTodos(dispatch, getState) {
    return getService(getState).getTodos()
      .then(todos => dispatch(setTodos(todos)))
  }
}

export const createTodo = (todo) => {
  return (dispatch, getState) => {
    return getService(getState).createTodo(todo)
      .then((newTodo) => dispatch(appendTodo(newTodo)))
  }
}

export const updateTodo = (todo) => {
  return (dispatch, getState) => {
    return getService(getState).updateTodo(todo)
      .then((newTodo) => dispatch(replaceTodo(newTodo)))
  }
}

export const deleteTodo = (id) => {
  return (dispatch, getState) => {
    return getService(getState).deleteTodo(id)
      .then(() => dispatch(excludeTodo(id)))
  }
}
