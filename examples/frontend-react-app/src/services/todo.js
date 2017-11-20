import { Service } from '../utils/services'


class TodoService extends Service {
  getTodos() {
    return this
      .api('todo')
      .get('/todos/')
      .auth('bearer')
      .then(res => this.json_if(res, 200))
  }

  createTodo(todo) {
    return this
      .api('todo')
      .post('/todos/')
      .body(todo)
      .auth('bearer')
      .then(res => this.json_if(res, 201))
  }

  updateTodo(todo) {
    return this
      .api('todo')
      .put(`/todos/${todo.id}/`)
      .body(todo)
      .auth('bearer')
      .then(res => this.json_if(res, 200))
  }

  deleteTodo(id) {
    return this
      .api('todo')
      .delete(`/todos/${id}/`)
      .auth('bearer')
      .then(res => this.throw_if_not(res, 204))
  }
}

export default TodoService;
